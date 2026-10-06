from difflib import SequenceMatcher
from rapidfuzz import fuzz, process
import json
from pathlib import Path
from normalize import normalize_arabic
from i18n import notify, t

file_path = Path("Database") / "quran_normalized.json"
hadith_file_path = Path("Database") / "hadith_normalized.json"

if file_path.exists():
    with open(file_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

if hadith_file_path.exists():
        with open(hadith_file_path, 'r', encoding="utf-8") as f:
            hadith_dataset = json.load(f)
    
    


WINDOW_SIZE = 40       
WINDOW_STEP = 10       
RETRIEVAL_WORDS = 30  
MAX_VERIFY_WORDS = 150 


def window_starts(n_words: int) -> list:

    if n_words <= WINDOW_SIZE:
        return [0]
    starts = list(range(0, n_words - WINDOW_SIZE + 1, WINDOW_STEP))
    if starts[-1] != n_words - WINDOW_SIZE:
        starts.append(n_words - WINDOW_SIZE)
    return starts


hadith_windows = []      
hadith_window_map = []   

for idx, h in enumerate(hadith_dataset):
    words = h["norma_text"].split()
    for start in window_starts(len(words)):
        hadith_windows.append(" ".join(words[start:start + WINDOW_SIZE]))
        hadith_window_map.append(idx)



from bisect import bisect_right

HADITH_SEP = " | "      # never appears in normalized text
hadith_blob = HADITH_SEP.join(h["norma_text"] for h in hadith_dataset)
hadith_offsets, _pos = [], 0
for _h in hadith_dataset:
    hadith_offsets.append(_pos)
    _pos += len(_h["norma_text"]) + len(HADITH_SEP)


def exact_hadith_indices(query: str, max_hits: int = 5) -> list:
    """Indices of hadith whose normalized text contains `query` on WORD boundaries
    (a single attached prefix letter و/ف/ب/ل/ك on the first word is tolerated)."""
    hits, start = [], 0
    while len(hits) < max_hits:
        k = hadith_blob.find(query, start)
        if k == -1:
            break
        idx = bisect_right(hadith_offsets, k) - 1
        end = k + len(query)
        end_ok = end >= len(hadith_blob) or hadith_blob[end] in " |"
        before = hadith_blob[k - 1] if k > 0 else " "
        before2 = hadith_blob[k - 2] if k > 1 else " "
        start_ok = before in " |" or (before in "وفبلك" and before2 in " |")
        if end_ok and start_ok and idx not in hits:
            hits.append(idx)
        start = hadith_offsets[idx + 1] if idx + 1 < len(hadith_offsets) else len(hadith_blob)
    return hits


def find_exact(input_user:str, quran_data:str, min_word=3, status_callback=None):
    
    def update_status(msg):
        if status_callback:
            status_callback(msg)
    
    text_user = normalize_arabic(input_user)
    words = text_user.split()
    
    
    if len(words) < min_word:
        return []
    
    results = []
    for ayah in quran_data:
        
        quran_normalized = ayah["norma_text"]
        
        if text_user in quran_normalized:
            
            match_type = "Exact Match Found" if text_user == quran_normalized else "Partial Match Found"
            
            results.append({
                "Surah Name": ayah["surah_name"],
                "Surah Number": ayah["surah_number"],
                "Ayah Number": ayah["ayah_number"],
                "Ayah": ayah["text"],
                "Match" : match_type
            })
            
    return results

quran_normalized = [ayah["norma_text"] for ayah in dataset]
hadith_normalized = [h["norma_text"] for h in hadith_dataset]

def find_hadith_fuzzy(
    user_input: str, limit: int = 5, candidate_pull_size: int = 60,
    min_word: int = 3, threshold: int = 85, status_callback=None,
    retrieval_words: int = RETRIEVAL_WORDS,
) -> list:
    
    
    normalized_input = normalize_arabic(user_input)
    user_words = normalized_input.split()

    if len(user_words) < min_word or not hadith_dataset:
        if status_callback:
            status_callback(t("status_too_short"))
        return []

    user_words = user_words[:MAX_VERIFY_WORDS]
    normalized_input = " ".join(user_words)

    # fast path: the quote is a verbatim piece of one or more hadith
    exact_hits = exact_hadith_indices(normalized_input)
    if exact_hits:
        out = []
        for idx in exact_hits:
            h = hadith_dataset[idx]
            out.append({"source_type": "hadith", "source_book": h["source"],
                        "hadith_number": h["hadith_number"], "text": h["text"],
                        "text_normalized": h["norma_text"], "score": 100.0,
                        "coverage": 1.0, "differences": [], "match_type": "matched"})
        return out[:limit]

    retrieval_query = " ".join(user_words[:retrieval_words])
    matches = process.extract(
        retrieval_query,
        hadith_windows,
        scorer=fuzz.partial_ratio,
        limit=candidate_pull_size,
    )

    results = []
    seen_indices = set()
    for item in matches:
        
        window_index = item[2]
        original_index = hadith_window_map[window_index]
        
        if original_index in seen_indices:
            continue
        seen_indices.add(original_index)

        h_data = hadith_dataset[original_index]
        score = item[1]
        
        hadith_words = h_data["norma_text"].split()
        matcher = SequenceMatcher(None, user_words, hadith_words)        

        diffs = []
        
        for tag,i1,i2,j1,j2 in matcher.get_opcodes():
            
            if tag in ("replace", "delete"):
                
                diffs.append({
                    "type": tag,
                    "user_words": user_words[i1:i2],
                    "hadith_words": hadith_words[j1:j2]
                })
            
            elif tag == "insert" and (0 < i1 and i2 < len(user_words)):
                
                diffs.append({
                    "type":tag,
                    "user_words":user_words[i1:i2],
                    "hadith_words":hadith_words[j1:j2]
                })       
                
                
        matching_words = sum(b.size for b in matcher.get_matching_blocks())
        
        coverage = matching_words / len(user_words) if user_words else 0
        
        if score == 100 and len(diffs) == 0 and coverage >= 0.7:
            
            status = 'matched'
        elif score >= threshold and coverage >= 0.7:
            status = "matched_with_diff"
            
        else:
            status = "no_reference"
            
        h_data= hadith_dataset[original_index]
        
        results.append({
            "source_type": "hadith",
            "source_book": h_data["source"],
            "hadith_number": h_data["hadith_number"],
            "text": h_data["text"],
            "text_normalized": h_data["norma_text"],
            "score": score,
            "coverage": round(coverage, 2),
            "differences": diffs,
            "match_type": status
        })
        
    results.sort(key=lambda x: (x["coverage"], x["score"]), reverse=True)
    return results[:limit]
    
    
    
def find_fuzzy(user_input:str, quran_normalized=quran_normalized, limit=3, candidate_pool_size:int = 60, min_word:int = 3, status_callback=None, threeshold: int = 80) -> list:
    
    normalized_input = normalize_arabic(user_input)
    user_words = normalized_input.split()
    
    if len(user_words) < min_word:
        if status_callback:
            status_callback(t("status_too_short"))
        return []
        

    matches = process.extract(
        normalized_input, 
        quran_normalized,
        scorer = fuzz.partial_ratio,
        limit = candidate_pool_size
    )
    
    results = []
    for ayah in matches:
        ayah_words = ayah[0].split()
        index = ayah[2]
        score = ayah[1]
        matcher = SequenceMatcher(None, user_words, ayah_words)
        diffs = []
        
        ayah_data = dataset[index]
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                pass
            elif tag in ("replace", "delete"):
                diffs.append({
                    "type": tag,
                    "user_words": user_words[i1:i2],
                    "ayah_words": ayah_words[j1:j2]
                })
            elif tag == "insert":
                if 0 < i1 and i2 < len(user_words):
                    diffs.append({
                        "type": tag,
                        "user_words": user_words[i1:i2],
                        "ayah_words": ayah_words[j1:j2]
                    })

        matching_words = sum(block.size for block in matcher.get_matching_blocks())
        coverage = matching_words / len(user_words) if user_words else 0

        if score == 100 and len(diffs) == 0 and coverage >= 0.7:
            status = "matched"
        elif score >= threeshold and coverage >= 0.7:
            status = "matched_with_diff"
        else:
            status = "no_reference"
                
        results.append({
            "surah_name": ayah_data["surah_name"],
            "surah_number": ayah_data["surah_number"],
            "ayah_number": ayah_data["ayah_number"],
            "text": ayah_data["text"],
            "text_normalized": ayah_data["norma_text"],
            "score": ayah[1],
            "coverage": round(coverage, 2),
            "differences": diffs,
            "match_type": status
        })
        
    results.sort(key=lambda x: (x["coverage"], x["score"]), reverse=True)
    return results[:limit]
                
def verify_quote(quote:str, status_callback=None, min_word:int = 3, threshold: int = 80):
    words = normalize_arabic(quote).split()
    
    if len(words) < min_word:
        
        return {
            "status" : "too_short", "source_type":None, "best_match" : None, "all_candidate" : []
        }
            
    quran_results = find_fuzzy(quote, min_word=min_word, threeshold=threshold)
    hadith_results = find_hadith_fuzzy(quote, min_word=min_word, threshold=threshold)
    
    best_quran = quran_results[0] if quran_results else None
    best_hadith = hadith_results[0] if hadith_results else None
    

    valid_quran = best_quran if (best_quran and best_quran["match_type"] in ["matched", "matched_with_diff"]) else None
    valid_hadith = best_hadith if (best_hadith and best_hadith["match_type"] in ["matched", "matched_with_diff"]) else None

    if valid_quran and valid_hadith:
        if (valid_hadith["coverage"], valid_hadith["score"]) > (valid_quran["coverage"], valid_quran["score"]):
            final_match = valid_hadith
            source_type = "hadith"
        else:
            final_match = valid_quran
            source_type = "quran"
    elif valid_quran:
        final_match = valid_quran
        source_type = "quran"
    elif valid_hadith:
        final_match = valid_hadith
        source_type = "hadith"
    else:
        final_match = None
        source_type = "none"
        
    final_status = final_match["match_type"] if final_match else "no_reference"
    
    
    if status_callback:
        status_callback(t(f"status_{final_status}"))
        
    return {
        "status": final_status,
        "source_type": source_type,
        "best_match": final_match,
        "all_candidates": quran_results + hadith_results
    }


if __name__ == "__main__":
    
    verify_quote("إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى")
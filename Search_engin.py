
from difflib import SequenceMatcher
from rapidfuzz import fuzz, process
import json
from pathlib import Path
from normalize import normalize_arabic
from i18n import notify, t

file_path = Path("Database") / "quran_normalized.json"

with open(file_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)
    
    
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


def find_fuzzy(user_input:str, quran_normalized=quran_normalized, limit=3, min_word:int = 3,status_callback=None) -> list:
    
    normalized_input = normalize_arabic(user_input)
    
    user_words= normalized_input.split()
    
    if len(user_words) < min_word:
        if status_callback:
            status_callback(t("status_too_short"))
        return []
        

    matches = process.extract(
        normalized_input, 
        quran_normalized,
        scorer = fuzz.partial_ratio,limit=limit
    )
    
    results= []
    for ayah in matches:
        ayah_words = ayah[0]
        ayah_words = ayah_words.split()
        index = ayah[2]
        score = ayah[1]
        matcher = SequenceMatcher(None, user_words, ayah_words)
        diffs = []
        
        ayah_data= dataset[index]
        for tag, i1,i2,j1,j2 in matcher.get_opcodes():
            
            if tag == "equal":
                pass
            elif tag in ("replace", "delete"):
                diffs.append({
                    "type":tag,
                    "user_words": user_words[i1:i2],
                    "ayah_words":ayah_words[j1:j2]
                })
                            
            elif tag == "insert":
                if 0 < i1 and i2 < len(user_words):
                    diffs.append({
                        "type":tag,
                        "user_words":user_words[i1:i2],
                        "ayah_words":ayah_words[j1:j2]
                    })
                    
        if score == 100 and len(diffs) == 0:
            status = "matched"
        elif score >= 80 :
            status = "matched_with_diff"
        else:
            status = "no_reference"
                
                
        results.append({
            "surah_name": ayah_data["surah_name"],
            "surah_number": ayah_data["surah_number"],
            "ayah_number": ayah_data["ayah_number"],
            "text": ayah_data["text"],
            "text_normalized":ayah_data["norma_text"],
            "score": ayah[1],
            "differences":diffs ,
            "match_type": status
        })
        
    return results
                
def verify_quote(quote:str, status_callback=None, min_word:int = 3):
    words = normalize_arabic(quote).split()
    
    if len(words) < min_word:
        
        final_status = "too_short"
        results= []
    else:
        results = find_fuzzy(quote, min_word=min_word)
        final_status = results[0]["match_type"] if results else "no_reference"
            
    if status_callback:
            status_callback(t(f"status_{final_status}"))
            
    return {
        "status": final_status,
        "best_match": results[0] if results else None ,
        "all_candidates": results 
    }


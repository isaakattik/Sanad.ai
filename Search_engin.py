
from difflib import SequenceMatcher
from rapidfuzz import fuzz, process
import json
from pathlib import Path
from build_normalized import normalize_arabic

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


def find_fuzzy(user_input:str, quran_normalized=quran_normalized, limit=3) -> list:
    
    normalized_input = normalize_arabic(user_input)
    
    user_words= normalized_input.split()
    
    
    matches = process.extract(
        normalized_input, 
        quran_normalized,
        scorer = fuzz.partial_ratio,limit=3
    )
    
    results= []
    for ayah in matches:
        ayah_words = ayah[0]
        ayah_words = ayah_words.split()
        index = ayah[2]
        matcher = SequenceMatcher(None, user_words, ayah_words)
        diffs = []
        
        ayah_data= dataset[index]
        for tag, i1,i2,j1,j2 in matcher.get_opcodes():
            
            if tag != "equal":
                diffs.append({
                    "type":tag,
                    "user_words": user_words[i1:i2],
                    "ayah_words":ayah_words[j1:j2]
                })
                
                
        results.append({
            "surah_name": ayah_data["surah_name"],
            "surah_number": ayah_data["surah_number"],
            "ayah_number": ayah_data["ayah_number"],
            "text": ayah_data["text"],
            "text_normalized":ayah_data["norma_text"],
            "score": matches[1],
            "Differences":diffs
        })
        
    return results
                

            
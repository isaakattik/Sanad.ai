

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
        print(f"⚠️ Search query is too short. Please enter at least {min_word} words.")
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
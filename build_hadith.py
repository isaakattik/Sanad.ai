

import json
from pathlib import Path
# from dotenv import url_api_hadith_link
import requests
from normalize import normalize_arabic
import re

HADITH_EDITIONS = {
    "صحيح البخاري": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/ara-bukhari.json",
    "صحيح مسلم": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/ara-muslim.json",
    "الأربعون النووية": "https://raw.githubusercontent.com/fawazahmed0/hadith-api/1/editions/ara-nawawi.json"
}

remove_control_chars = re.compile(r"[\u200f\u200e\ufeff\u200b\u200c\u200d\u202a-\u202e]")


def clean_raw_text(text:str) -> str:
    
    if not text:
        return ""
    
    text = remove_control_chars.sub("", text)
    
    return re.sub(r"\s+", " ", text).strip()

def buid_hadith_dataset():
    
    output_path = Path("Dataset") / "hadith_normalized.json"
    
    if output_path.exists():
        print(f"The File already Exists in {output_path}, Skipping Loading.")
        return
    
    
    print(f"⏳ Downloading the Three Books of Prophetic Hadith app... ")
    
    all_hadiths = []
    
    for source_name , url in HADITH_EDITIONS.items():
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        count = 0
        
        for item in data.get("hadiths", []):
            raw_text = item.get("text", "").strip() 
            clean_text = clean_raw_text(raw_text)
            if not clean_text:
                continue
            
            
            all_hadiths.append({
                "source":source_name, "hadith_number": item.get("hadithnumber"), "text": clean_text, "norma_text": normalize_arabic(clean_text)
                                })
            count +=1
            
            print(f"✔️ تم معالجة {count} حديث من {source_name}")
            
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_hadiths, f, ensure_ascii=False, indent=2)
        
    print(f"🎉 تم حفظ إجمالي {len(all_hadiths)} حديث في {output_path}")
        
if __name__ == "__main__":
    buid_hadith_dataset()
            
            
            
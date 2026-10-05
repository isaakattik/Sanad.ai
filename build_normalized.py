

import json
from normalize import normalize_arabic
from pathlib import Path
from i18n import notify

def build_normalized_dataset(
    normalize_arabic= normalize_arabic,file_read="quran.json",status_callback=None
    ):
    
    
    folder_name = Path("Database")
    file_path = Path("Database") / file_read

    with open (file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for ayah in data:
        normalize= normalize_arabic(ayah["text"])
        ayah["norma_text"] = normalize
        
    output_path = folder_name / "quran_normalized.json"
    
    
    if output_path.exists():
        notify(status_callback,"file_exists",file_path = output_path)
    else:
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    build_normalized_dataset()



import json
from normalize import normalize_arabic
from pathlib import Path


folder_name = Path("Database")

file_path = folder_name / "quran.json"

with open (file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    
for ayah in data:
    normalize= normalize_arabic(ayah["text"])
    ayah["norma_text"] = normalize
    
    
output_path = folder_name / "quran_normalized.json"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)
    

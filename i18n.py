

import json
from pathlib import Path

current_lang= "ar"

def f(key:str) ->str:
    
    locales_dir = Path("locals")
    
    file_path = locales_dir / f"{current_lang}.json"
    
    if file_path.exists():
        with open(file_path, 'r', encoding="utf-8") as f:
            translations = json.load(f)
            return translations.get(key,key)
        
        return key
            
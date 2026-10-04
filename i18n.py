

import json
from pathlib import Path

current_lang= "ar"
_cached_translations = {}    

def load_translations():
    global _cached_translations
    file_path = Path("locales") / f"{current_lang}.json"
    
    if file_path.exists():
        with open(file_path, 'r', encoding="utf-8") as f:
            _cached_translations = json.load(f)
    else:
        _cached_translations = {}
        
        
def set_language(lang_code: str):
    global current_lang
    current_lang = lang_code
    load_translations()


def t(key:str, **kwargs) ->str: 
    
    if not _cached_translations:
        load_translations()
        
    text = _cached_translations.get(key, key)
    
    if kwargs:
        return text.format(**kwargs)
    
    return text
    
def notify(callback, key, **kwargs):
    msg = t(key, **kwargs)
     
    if callback:
        callback(msg)
    return msg
        

    
    
            
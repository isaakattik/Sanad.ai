import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from i18n import notify
load_dotenv()

API_URL = os.getenv("quran_data_api_link")


def recive_data(url=API_URL, output_file="quran.json", status_callback=None):
    def update_status(msg):
        if status_callback:
            status_callback(msg)
            
    def clean_ayah_text(text, surah_number, ayah_in_surah):
        
        BASMALA = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
        text = text.replace("\ufeff","")
        
        if ayah_in_surah == 1 and surah_number not in (1,9):
            
            if text.startswith(BASMALA):
                
                text = text.removeprefix(BASMALA).strip()
        return text

    folder_path = Path("Database")
    file_path = folder_path / output_file

    if file_path.exists():
        notify(status_callback,"file_exists",file_path = file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    notify(status_callback, "start_downlaod")
    response = requests.get(url or API_URL)
    response.raise_for_status()

    payload = response.json()
    if payload.get("code") != 200:
        notify(status_callback,"api_failed",status= payload.get("status"))
        return None

    quran_data = []
    for surah in payload["data"]["surahs"]:
        
        
        for ayah in surah["ayahs"]:
            cleaned_text = clean_ayah_text(
                ayah["text"],
                surah["number"],
                ayah["numberInSurah"]
            )
            quran_data.append({
                "surah_number": surah["number"],
                "surah_name": surah["name"],
                "ayah_number": ayah["numberInSurah"],
                "ayah_global": ayah["number"],
                "text": cleaned_text,
            })

    folder_path.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(quran_data, f, ensure_ascii=False, indent=2)

    notify(status_callback,"download_complet", count=len(quran_data),file_path=file_path)
    return quran_data


if __name__ == "__main__":
    recive_data(status_callback=print)
    
data = recive_data(status_callback=print)


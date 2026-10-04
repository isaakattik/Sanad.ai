import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("quran_data_api_link")


def recive_data(url=API_URL, output_file="quran.json", status_callback=None):
    def update_status(msg):
        if status_callback:
            status_callback(msg)

    folder_path = Path("Database")
    file_path = folder_path / output_file

    if file_path.exists():
        update_status(f"File already exists at {file_path}. Skipping download.")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    update_status("Starting download...")
    response = requests.get(url or API_URL)
    response.raise_for_status()

    payload = response.json()
    if payload.get("code") != 200:
        update_status(f"API request failed: {payload.get('status')}")
        return None

    quran_data = []
    for surah in payload["data"]["surahs"]:
        for ayah in surah["ayahs"]:
            quran_data.append({
                "surah_number": surah["number"],
                "surah_name": surah["name"],
                "ayah_number": ayah["numberInSurah"],
                "ayah_global": ayah["number"],
                "text": ayah["text"],
            })

    folder_path.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(quran_data, f, ensure_ascii=False, indent=2)

    print(payload["data"]["surahs"][0]["ayahs"][0].keys())
    update_status(f"Saved {len(quran_data)} ayahs to {file_path}")
    return quran_data


if __name__ == "__main__":
    recive_data(status_callback=print)
    
data = recive_data(status_callback=print)
print(data[-1])



# import random as rm
import json
from pathlib import Path

quran_json_file_path = Path("Database") / "quran_normalized.json"

def read_json_data(file_path= quran_json_file_path):
    
    with open(file_path , 'r', encoding='utf-8') as f:
        data_quran = json.load(f)
        
    return data_quran


def creating_test():
    
    text_quran = read_json_data()["text"]
    return text_quran
    
    
if __name__ == "__main__":
    creating_test()
    
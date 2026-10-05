

import random as rm
import json
from pathlib import Path

rm.seed(42)
quran_json_file_path = Path("Database") / "quran_normalized.json"

def read_json_data(file_path= quran_json_file_path):
    
    with open(file_path , 'r', encoding='utf-8') as f:
        data_quran = json.load(f)
        
    return data_quran

def generate_random_ayahs():
    
    quran_data = read_json_data()
    text_quran = [ayah["text"] for ayah in quran_data]
    text_norma_quran = [ayah["norma_text"] for ayah in quran_data]
    
    counter = 0
    matched_type = []
    matched_diff_type = []

        
    while len(matched_diff_type) < 15 and len(matched_type) < 15:
        random_id_1 = rm.randint(1, len(quran_data))
        random_id_2 = rm.randint(1, len(quran_data))
        

        added_to_first = False
        added_to_second = False
        

        temp_first = None
        temp_second = None

        for ayah in quran_data:

            if ayah.get("ayah_global") == random_id_1:
                ayah_words = ayah["text"].split()
                if counter < 5:
                    temp_first = ayah["text"]
                elif counter < 10:
                    if counter < 8:
                        temp_first = " ".join(ayah_words[2:7])
                    else:
                        temp_first = " ".join(ayah_words[:5])
                else:
                    temp_first = ayah["norma_text"]
                added_to_first = True
                

            if ayah.get("ayah_global") == random_id_2:
                verse_words = ayah["text"].split()
                words_notashkil = ayah["norma_text"].split()
                
                if len(verse_words) >= 6:
                    index = rm.randint(2, len(verse_words)-2)
                    
                    if counter < 5:
                        verse_words.pop(index)
                        temp_second = " ".join(verse_words)
                    elif counter < 10:
                        verse_words[index] = "رَزَقْنَاكُمْ"
                        temp_second = " ".join(verse_words)
                    else:
                        verse_words.insert(index, "فَقَالُوا هَٰذَا")
                        temp_second = " ".join(verse_words)
                    added_to_second = True


        if added_to_first and added_to_second:
            matched_type.append(temp_first)
            matched_diff_type.append(temp_second)
            counter += 1
                    
            
            

    return matched_type ,matched_diff_type
            
fabricated_samples = [
    "إنما الأعمال بالنيات وإنما لكل امرئ ما نوى",
    "طلب العلم فريضة على كل مسلم ومسلمة",
    "من غشنا فليس منا",
    "خيركم من تعلم القرآن وعلمه",
    "الدين المعاملة والصدق أمانة",
    "وأقيموا العدل بينكم وتبينوا في أمركم",
    "إن الله يحب إذا عمل أحدكم عملا أن يتقنه",
    "لا تؤخر عمل اليوم إلى الغد",
    "اتق الله حيثما كنت وأتبع السيئة الحسنة تمحها",
    "المسلم من سلم المسلمون من لسانه ويده"
]

def write_in_file():
    
    all_cases= []
    matched_type , matched_diff_type = generate_random_ayahs()
    
    for text in matched_type:
        
        all_cases.append({
            "text":text,
            "expected_status":"matched",
            "type":"correct_quran"
        })
    
    for text in matched_diff_type:
            
            all_cases.append({
                "text":text,
                "expected_status":"matched_with_diff",
                "type":"modified_quran"
            })
            
    for text in fabricated_samples:
            
            all_cases.append({
                "text":text,
                "expected_status":"no_reference",
                "type":"fabricated"
            })
            
    output_file = Path("Database") / "test_set.json"
    
    
    if output_file.exists():
        print(f"File already exists at {output_file}. Skipping download.")
        
    else:
        with open(output_file, "w", encoding="utf-8") as file:
                    json.dump(all_cases, file, indent=4, ensure_ascii=False)
    
    
    
    
if __name__ == "__main__":
    
    write_in_file()   
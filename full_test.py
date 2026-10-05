

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
    
    matched_type = []
    matched_diff_type = []
    


    counter = 0
    while len(matched_type) < 15:
        ayah = rm.choice(quran_data)
        words = ayah["text"].split()
        
        if counter < 5:
            matched_type.append(ayah["text"])
            counter += 1
        elif counter < 10:
            if len(words) >= 6:
                partial_text = " ".join(words[1:6])
                matched_type.append(partial_text)
                counter += 1
        else:
            matched_type.append(ayah["norma_text"])
            counter += 1

    # 2. Modified Ayahs (15 cases)
    # Selected ayahs with len >= 6 words, modified in the middle
    counter = 0
    while len(matched_diff_type) < 15:
        ayah = rm.choice(quran_data)
        verse_words = ayah["text"].split()
        
        if len(verse_words) >= 6:
            index = rm.randint(1, len(verse_words) - 2)
            
            if counter < 5:
                # Delete a word
                verse_words.pop(index)
                matched_diff_type.append(" ".join(verse_words))
                counter += 1
            elif counter < 10:
                # Replace a word
                verse_words[index] = "رَزَقْنَاكُمْ"
                matched_diff_type.append(" ".join(verse_words))
                counter += 1
            else:
                # Insert a word
                verse_words.insert(index, "فَقَالُوا")
                matched_diff_type.append(" ".join(verse_words))
                counter += 1

    return matched_type, matched_diff_type

hadith_samples = [
    "إنما الأعمال بالنيات وإنما لكل امرئ ما نوى",
    "طلب العلم فريضة على كل مسلم ومسلمة",
    "من غشنا فليس منا",
    "خيركم من تعلم القرآن وعلمه",
    "الدين المعاملة والصدق أمانة",
    "إن الله يحب إذا عمل أحدكم عملا أن يتقنه",
    "لا تؤخر عمل اليوم إلى الغد",
    "اتق الله حيثما كنت وأتبع السيئة الحسنة تمحها",
    "المسلم من سلم المسلمون من لسانه ويده",
    "الطهور شطر الإيمان والحمد لله تملأ الميزان"
]

pseudo_quranic_samples = [
    "وأقيموا العدل بينكم وتبينوا في أمركم لعلكم ترحمون",
    "إن الله يعلم ما أسررتم وما أعلنتم من أمركم وإليه ترجعون",
    "يا أيها الذين آمنوا اتقوا الله وكونوا مع الصادقين في الأوفياء",
    "ولئن صبرتم على ما أصابكم إن ذلك من عزم الأمور في العالمين",
    "وقولوا للناس حسنا وأقيموا التراحم في بيوتكم ترحمون",
    "إن في اختلاف الليل والنهار لآيات لأولي الألباب والعقول الزكية",
    "وما الحياة الدنيا إلا متاع الزينة والغرور والافتتان",
    "فمن يعمل من الصالحات وهو مؤمن فلا كفران لجهده وتوفى نفسه",
    "سبحان الذي خلق السموات وبث فيها من كل دابة ورزقكم",
    "واصبر على ما يقولون واهجرهم هجرا جميلا إن الله عليم"
]

def write_in_file():
 
    all_cases = []
    matched_type, matched_diff_type = generate_random_ayahs()
    

    for text in matched_type:
        
        all_cases.append({
            "text": text,
            "expected_status": "matched",
            "type": "correct_quran"
        })
    
    for text in matched_diff_type:
        all_cases.append({
            "text": text,
            "expected_status": "matched_with_diff",
            "type": "modified_quran"
        })
    
    # Hadith / Wisdom (Not in Quran)
    for text in hadith_samples:
        all_cases.append({
            "text": text,
            "expected_status": "not_in_quran",
            "type": "hadith"
        })
        
    # Pseudo-Quranic fabricated (Not in Quran)
    for text in pseudo_quranic_samples:
        all_cases.append({
            "text": text,
            "expected_status": "not_in_quran",
            "type": "pseudo_quran"
        })
            
    output_file = Path("Database") / "test_set.json"
    
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_cases, file, indent=4, ensure_ascii=False)
        
    print(f"✅ Generated {len(all_cases)} test cases into {output_file}")

if __name__ == "__main__":
    
    write_in_file()   

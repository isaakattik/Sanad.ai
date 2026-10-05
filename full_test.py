import random as rm
import json
from pathlib import Path

rm.seed(42)
quran_json_file_path = Path("Database") / "quran_normalized.json"

def read_json_data(file_path=quran_json_file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_random_ayahs():
    quran_data = read_json_data()
    
    matched_type = []
    matched_diff_type = []
    


    counter = 0
    while len(matched_type) < 15:
        ayah = rm.choice(quran_data)
        words = ayah["text"].split()
        
        if counter < 5:
            if len(words) >= 3:
                matched_type.append(ayah["text"])
                counter += 1
        elif counter < 10:
            if len(words) >= 7:
                partial_text = " ".join(words[2:7])
                matched_type.append(partial_text)
                counter += 1
        else:
            if len(words) >= 3:
                matched_type.append(ayah["norma_text"])
                counter += 1


    counter = 0
    while len(matched_diff_type) < 15:
        ayah = rm.choice(quran_data)
        verse_words = ayah["text"].split()
        
        if len(verse_words) >= 7:
            index = rm.randint(2, len(verse_words) - 2)
            
            if counter < 5:

                verse_words.pop(index)
                matched_diff_type.append(" ".join(verse_words))
                counter += 1
            elif counter < 10:

                verse_words[index] = "رَزَقْنَاكُمْ"
                matched_diff_type.append(" ".join(verse_words))
                counter += 1
            else:

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
    "وأقيموا العدل والتراحم في أسركم لعلكم تصبحون",
    "إن الله يعلم ما تسرون في قلوبكم وإليه مصيركم أجمعين",
    "يا أيها الناس اتقوا ربكم وكونوا مع الصديقين في أفعالهم",
    "ولئن ثبتتم على الحق إن ذلك من خير الأعمال للعباد",
    "وقولوا قولا سديدا وأصلحوا ذات بينكم في مساكنكم",
    "إن في تقلب الليل والنهار لعلامات لأهل النظر والتفكر",
    "وما الحياة الدنيا إلا دار الابتلاء والتمحيص للبشر",
    "فمن يفعل الطيبات وهو مؤمن فلا ضياع لجهده عند ربه",
    "سبحان الذي أبدع السموات وأنزل فيها من كل بركة",
    "واصبر على ما ينالك واصفح الصفح الجميل عن الجميع"
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
    

    for text in hadith_samples:
        all_cases.append({
            "text": text,
            "expected_status": "not_in_quran",
            "type": "hadith"
        })
        

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

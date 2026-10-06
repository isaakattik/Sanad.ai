import random as rm
import json
from pathlib import Path

rm.seed(42)
quran_json_file_path = Path("Database") / "quran_normalized.json"
hadith_json_file_path = Path("Database") / "hadith_normalized.json"

with open(quran_json_file_path, 'r', encoding='utf-8') as f:
    quran_data = json.load(f)

with open(hadith_json_file_path, 'r', encoding='utf-8') as f:
    hadith_data = json.load(f)

def generate_random_ayahs():
    matched_type = []
    matched_diff_type = []
    
    # 15 Correct Quran Ayahs
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

    # 15 Modified Quran Ayahs
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


def generate_random_hadiths():
    correct_hadiths = []
    modified_hadiths = []
    
    # 10 Correct Hadiths
    while len(correct_hadiths) < 10:
        item = rm.choice(hadith_data)
        words = item["text"].split()
        if len(words) >= 6:
            correct_hadiths.append(item["text"])
            
    # 10 Modified Hadiths
    while len(modified_hadiths) < 10:
        item = rm.choice(hadith_data)
        words = item["text"].split()
        if len(words) >= 8:
            idx = rm.randint(2, len(words) - 2)
            words.pop(idx) # Delete a word in the middle of Hadith
            modified_text = " ".join(words)
            modified_hadiths.append(modified_text)
            
    return correct_hadiths, modified_hadiths

# 10 Famous Hadith Quotes (Correct Hadith)
famous_hadith_samples = [
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

# 10 Pseudo-Quranic fabricated quotes (Not in Quran or Hadith)
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

# 10 General Non-Religious / Fabricated Phrases (Not in Quran or Hadith)
general_fabricated_samples = [
    "القراءة تغذي العقل وتوسع مدارك الإنسان في الحياة",
    "الرياضة تنشط الجسم وتحافظ على الصحة السليمة",
    "التكنولوجيا الحديثة غيّرت أسلوب التواصل بين البشر",
    "العمل الجماعي يحقق النجاح والتفوق في المؤسسات",
    "التعليم هو الأساس لبناء المجتمعات المتقدمة والراقية",
    "الصبر والاجتهاد هما مفتاح النجاح في جميع المجالات",
    "الحفاظ على البيئة واجب على كل مواطن في المجتمع",
    "السفر يفتح آفاقا جديدة للتعلم واكتساب الخبرات",
    "التخطيط الجيد يساعد على إنجاز الأهداف بدقة وفاعلية",
    "احترام الآخرين يعكس أخلاق الإنسان وتربيته الحسنة"
]

def write_in_file():
    all_cases = []
    
    matched_type, matched_diff_type = generate_random_ayahs()
    correct_hadiths, modified_hadiths = generate_random_hadiths()


    for text in matched_type:
        all_cases.append({
            "text": text,
            "expected_status": "matched",
            "expected_source": "quran",
            "type": "correct_quran"
        })
    

    for text in matched_diff_type:
        all_cases.append({
            "text": text,
            "expected_status": "matched_with_diff",
            "expected_source": "quran",
            "type": "modified_quran"
        })


    for text in correct_hadiths:
        all_cases.append({
            "text": text,
            "expected_status": "matched",
            "expected_source": "hadith",
            "type": "correct_hadith"
        })
        
    for text in famous_hadith_samples:
        all_cases.append({
            "text": text,
            "expected_status": "matched",
            "expected_source": "hadith",
            "type": "famous_hadith"
        })


    for text in modified_hadiths:
        all_cases.append({
            "text": text,
            "expected_status": "matched_with_diff",
            "expected_source": "hadith",
            "type": "modified_hadith"
        })


    for text in pseudo_quranic_samples:
        all_cases.append({
            "text": text,
            "expected_status": "no_reference",
            "expected_source": "none",
            "type": "pseudo_quran"
        })

    for text in general_fabricated_samples:
        all_cases.append({
            "text": text,
            "expected_status": "no_reference",
            "expected_source": "none",
            "type": "general_fabricated"
        })

    output_file = Path("Database") / "test_set.json"
    
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_cases, file, indent=4, ensure_ascii=False)
        
    print(f"✅ Generated {len(all_cases)} test cases with expected_source into {output_file}")

if __name__ == "__main__":
    write_in_file()

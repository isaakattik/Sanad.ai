import json
from pathlib import Path
from Search_engin import verify_quote

def run_evaluation(threshold: int = 85):
    dataset_path = Path("Database") / "test_set.json"
    
    with open(dataset_path, 'r', encoding="utf-8") as f:
        test_cases = json.load(f)
        
    correct_quran_matches = 0   
    correct_hadith_matches = 0  
    detected_modified = 0       
    safe_miss = 0               
    false_acceptances = 0    
    correct_rejections = 0      
    correct_source_predictions = 0 

    total_quran_correct = 0
    total_hadith_correct = 0
    total_modified = 0
    total_fabricated = 0

    total_cases = len(test_cases)

    for i, case in enumerate(test_cases):
        expected_status = case["expected_status"]
        expected_source = case.get("expected_source", "none")
        
        result = verify_quote(case["text"], threshold=threshold)
        actual_status = result["status"]
        actual_source = result.get("source_type") if result.get("source_type") else "none"
        
        if (i + 1) % 10 == 0 or (i + 1) == total_cases:
            print(f"⏳ Processed [{i+1}/{total_cases}] test cases...", flush=True)


        if expected_source == actual_source:
            correct_source_predictions += 1
            

        if expected_source == "quran" and expected_status == "matched":
            total_quran_correct += 1
            if actual_status == "matched" and actual_source == "quran":
                correct_quran_matches += 1


        elif expected_source == "hadith" and expected_status == "matched":
            total_hadith_correct += 1
            if actual_status == "matched" and actual_source == "hadith":
                correct_hadith_matches += 1


        elif expected_status == "matched_with_diff":
            total_modified += 1
            if actual_status == "matched_with_diff":
                detected_modified += 1
            elif actual_status == "matched":
                false_acceptances += 1
            elif actual_status == "no_reference":
                safe_miss += 1


        elif expected_status == "no_reference":
            total_fabricated += 1
            if actual_status in ["matched", "matched_with_diff"]:
                false_acceptances += 1
            elif actual_status == "no_reference":
                correct_rejections += 1

    total_non_exact = total_modified + total_fabricated
    
    far_rate = (false_acceptances / total_non_exact) * 100 if total_non_exact > 0 else 0
    quran_crr = (correct_quran_matches / total_quran_correct) * 100 if total_quran_correct > 0 else 0
    hadith_chr = (correct_hadith_matches / total_hadith_correct) * 100 if total_hadith_correct > 0 else 0
    detection_rate = (detected_modified / total_modified) * 100 if total_modified > 0 else 0
    rejection_rate = (correct_rejections / total_fabricated) * 100 if total_fabricated > 0 else 0
    source_acc = (correct_source_predictions / total_cases) * 100 if total_cases > 0 else 0

    print(f"\n================ 📊 تقرير القياس الشامل (العتبة = {threshold}) ================", flush=True)
    print(f"🎯 دقة تحديد المصدر (Quran vs Hadith): {source_acc:.2f}% ({correct_source_predictions}/{total_cases})", flush=True)
    print(f"🔴 القبول الخاطئ (FAR): {far_rate:.2f}% ({false_acceptances}/{total_non_exact})", flush=True)
    print(f"🟢 مطابقة القرآن الصحيح: {quran_crr:.2f}% ({correct_quran_matches}/{total_quran_correct})", flush=True)
    print(f"🟢 مطابقة الأحاديث الصحيحة: {hadith_chr:.2f}% ({correct_hadith_matches}/{total_hadith_correct})", flush=True)
    print(f"🎯 كشف المحرَّف (قرآن + حديث): {detection_rate:.2f}% ({detected_modified}/{total_modified})", flush=True)
    print(f"🛡️ الفوات الآمن للمحرف: {safe_miss}/{total_modified}", flush=True)
    print(f"🟡 الامتناع (الرفض الصحيح للنصوص غير الموجودة): {rejection_rate:.2f}% ({correct_rejections}/{total_fabricated})", flush=True)
    print("========================================================================\n", flush=True)

if __name__ == "__main__":
    for th in [85]:
        run_evaluation(threshold=th)
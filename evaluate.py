

import json
from pathlib import Path
from Search_engin import verify_quote


def run_evaluation(threshold: int = 80):
    
    dataset_path = Path("Database") / "test_set.json"
    
    with open(dataset_path, 'r', encoding="utf-8") as f:
        
        test_cases = json.load(f)
        
    correct_matches = 0    
    detected_modified = 0     
    safe_miss = 0        
    false_acceptances = 0     
    correct_rejections = 0    

    total_correct = 0
    total_modified = 0
    total_non_quran = 0

    for case in test_cases:
        
        expected = case["expected_status"]
        
        result = verify_quote(case["text"],threshold=threshold)
        
        actual = result["status"]
        

        if expected == "matched":
            total_correct += 1
            
            if actual == "matched":
                correct_matches += 1


        elif expected == "matched_with_diff":
            total_modified += 1
            if actual == "matched_with_diff":
                detected_modified += 1
            elif actual == "matched":
                false_acceptances += 1
            elif actual == "no_reference":
                safe_miss += 1


        elif expected in ["no_reference", "not_in_quran"]:
            total_non_quran += 1
            if actual in ["matched", "matched_with_diff"]:
                false_acceptances += 1
            elif actual == "no_reference":
                correct_rejections += 1



    total_non_exact = total_modified + total_non_quran
    far_rate = (false_acceptances / total_non_exact) * 100 if total_non_exact > 0 else 0
    crr_rate = (correct_matches / total_correct) * 100 if total_correct > 0 else 0
    detection_rate = (detected_modified / total_modified) * 100 if total_modified > 0 else 0
    rejection_rate = (correct_rejections / total_non_quran) * 100 if total_non_quran > 0 else 0

    print(f"\n================ 📊 تقرير القياس (العتبة = {threshold}) ================")
    print(f"🔴 القبول الخاطئ (FAR): {far_rate:.2f}% ({false_acceptances}/{total_non_exact})")
    print(f"🟢 التعرف على الصحيح: {crr_rate:.2f}% ({correct_matches}/{total_correct})")
    print(f"🎯 كشف المحرَّف: {detection_rate:.2f}% ({detected_modified}/{total_modified})")
    print(f"🛡️ الفوات الآمن للمحرف: {safe_miss}/{total_modified}")
    print(f"🟡 الامتناع (الرفض الصحيح): {rejection_rate:.2f}% ({correct_rejections}/{total_non_quran})")
    print("========================================================================\n")

if __name__ == "__main__":
    for th in [80, 85, 90]:
        run_evaluation(threshold=th)
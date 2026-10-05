

import json
from pathlib import Path
from Search_engin import verify_quote


def run_evaluation(threshold: int = 80):
    
    dataset_path = Path("Database") / "test_set.json"
    
    with open(dataset_path, 'r', encoding="utf-8") as f:
        
        test_cases = json.load(f)
        
    false_acceptances = 0
    correct_matches =0
    correct_rejections = 0
    
    total_non_exact = 0
    total_correct = 0
    total_fabricated = 0
    
    
    for case in test_cases:
        
        expected = case["expected_status"]
        
        result = verify_quote(case["text"],threshold=threshold)
        
        actual = result["status"]
        
        
        if expected in ["matched_with_diff","no_reference"]  :
            
            total_non_exact += 1
            
            if expected == "matched_with_diff" and actual == "matched" :
                false_acceptances += 1
                
            elif expected == "no_reference" and actual in ["matched", "matched_with_diff"] :
                
                false_acceptances += 1
                
        elif expected == "matched":
            total_correct += 1
            
            if actual == "matched":
                correct_matches += 1
                
        elif expected == "no_reference":
            total_fabricated += 1
            if actual == "no_reference":
                correct_rejections += 1
                
                
    far_rate = (false_acceptances / total_non_exact) * 100 if total_non_exact > 0 else 0 
    correct_rate = (correct_matches / total_correct) * 100 if total_correct > 0 else 0 
    rejection_rate = (correct_rejections / total_fabricated) * 100 if total_fabricated > 0 else 0
    
    
    print(f"\n===== Raport Evaluation: Threshold = {threshold} =====")
    print(f"\n===== False Acceptance (FAR) : {far_rate:.2f}% , ({false_acceptances}/{total_non_exact})=====")
    print(f"\n===== Identifying the correct : {correct_rate:.2f}% , ({correct_matches}/{total_correct}) =====")
    print(f"\n===== Abstention (Valid Refusal) : {rejection_rate:.2f}% , ({correct_rejections}/{total_fabricated})=====")
             
             
             
if __name__ == "__main__":
    for th in [80, 85, 90]:
        run_evaluation(threshold=th)


import re

remove_marks = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED\u0640]")

not_arabic_letter = re.compile(r"[^\u0621-\u064A\s]")

multi_space = re.compile(r"\s+")


def normalize_arabic(text:str)-> str:
    
    text = remove_marks.sub("", text)                        
    text = re.sub(r"[\u0622\u0623\u0625\u0671]", "ا", text)  
    text = text.replace("ى", "ي")                          
    text = text.replace("ة", "ه")                          
    text = not_arabic_letter.sub(" ", text)                 
    text = multi_space.sub(" ", text).strip()                
    return text




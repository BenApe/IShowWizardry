import json
import random

def keygen(dict:dict):
    key = random.randint(0, 1000000)
    
    if key in dict:
        key = keygen(dict)
    
    return key
    
def break_lines(text:str, max_len:int, preserve_words:bool = True):
    lines = []
    curr_line = ""
    
    if preserve_words:
        words = text.split()
        
        for word in words:
            if len(curr_line) + len(word) + 1 <= max_len:
                if curr_line:
                    curr_line += " " + word
                
                else:
                    curr_line = word
            
            else:
                if curr_line:
                    lines.append(curr_line)
                    
                curr_line = word
        
        if curr_line:
            lines.append(curr_line)
    
    else:
        for char in text:
            if len(curr_line) >= max_len:
                lines.append(curr_line)
                curr_line = char
            
            else:
                curr_line += char
        
    return lines

def loadjson(file_name:str, int_keys:bool = True):
    file_path = f"{file_name}.json"
    data = {}
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            if isinstance(data, dict) and int_keys:
                data = {
                    int(key): value
                    for key, value in data.items()
                }
                
    except Exception as e:
        print(f"Error loading file {file_path}: {e}. Starting with an empty file.")
        
    return data

def savejson(file_name, data):
    file_path = f"{file_name}.json"
    
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
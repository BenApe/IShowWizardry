import json
import random

from datetime import datetime, timedelta
from pathlib import Path

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

def get_discord_timestamp(iso_time:str, style="R", increment_minutes:int = 0):
    """
    ### Styles:
    
    't' - Short time (e.g., 16:20)
    
    'T' - Long time (e.g., 16:20:30)
    
    'd' - Short date (e.g., 20/04/2021)
    
    'D' - Long date (e.g., 20 April 2021)
    
    'f' - Short date/time (e.g., 20 April 2021 16:20)
    
    'F' - Long date/time (e.g., Tuesday, 20 April 2021 16:20)
    
    'R' - Relative time (e.g., 2 hours ago, in 5 minutes)
    """
    original_time = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
    time = original_time + timedelta(minutes=increment_minutes)
    timestamp = int(time.timestamp())
    
    return f"<t:{timestamp}:{style}>"

def paginate(items: list, per_page: int):
    pages = []
    page_ct = len(items) // per_page
    
    for page_num in range(page_ct + 1):
        page = []
        for entry_num in range(per_page):
            try:
                n = (per_page * page_num) + entry_num
                entry = items[n]
                page.append(entry)
            except:
                break
        pages.append(page)
    
    return pages

def grab_filenames(dir: str = "."):
    folder = Path(dir)
    names = [str(f) for f in folder.iterdir() if f.is_file()]
    return names

def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    
    return f"{n}{suffix}"

class process_timer():
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.elapsed = 0
    
    def start(self):
        self.start_time = datetime.now()
    
    def end(self, description: str = None):
        self.end_time = datetime.now()
        delta = self.end_time - self.start_time
        self.elapsed = round(delta.total_seconds() * 1000)
        
        if description != None:
            print(f"{self.end_time.strftime("%d/%m/%Y %H:%M:%S")} | {description} ({self.elapsed}ms).")
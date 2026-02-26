import json
import random
import discord

from discord.ext import commands
from datetime import datetime, timedelta, timezone

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
    Styles:
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
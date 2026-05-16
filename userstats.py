import discord
import json

from botutils import loadjson, savejson, process_timer
from datetime import datetime
from discord import app_commands

STATS_PAGE_LEN = 50
DEFAULT_STATS = {
    "stars_recieved": 0,
    "board_msgs": 0,
    "fish_caught": 0,
    "times_pondered": 0
}
VALID_VALS = [
    "stars_recieved",
    "board_msgs",
    "fish_caught",
    "times_pondered"
]

def load_file_for_search(filepath: str):
    fp = f"{filepath}.json"
    with open(fp, 'r') as f:
        data = json.load(f)
    
    users = [(uid, stats) for uid, stats in data.items()]
    return users

def search_stats_files(user_id: int, num_files: int):
    first_file = load_file_for_search("user_data/stats/0")
    last_file = load_file_for_search(f"user_data/stats/{num_files - 1}")
    
    if not first_file:
        return None
    
    if num_files == 1:
        return search_in_file(user_id, first_file)
    
    if user_id < first_file[0][0] or user_id > last_file[-1][0]:
        return None
    
    left = 0
    right = num_files - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_file = load_file_for_search(f"user_data/stats/{mid}")
        
        first_id = int(mid_file[0][0])
        last_id = int(mid_file[0][0])
        
        if first_id <= user_id <= last_id:
            return search_in_file(user_id, mid_file)
        
        elif user_id < first_id:
            right = mid - 1
        
        else:
            left = mid + 1
    
    return None
            
def search_in_file(user_id: int, users: list):
    left = 0
    right = len(users) - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_id = int(users[mid][0])
        
        if mid_id == user_id:
            return users[mid][1]
        
        elif mid_id < user_id:
            left = mid + 1
        
        else:
            right = mid - 1
        
    return None

def collect_users(num_files: int):
    all_users = []
    
    for i in range(num_files):
        page_path = f"user_data/stats/{i}"
        stats_page = loadjson(page_path)
        
        for uid, stats in stats_page.items():
            all_users.append((uid, stats))
    
    all_users.sort(key=lambda x: x[0])
    return all_users

def sort_stats(num_files: int):
    timer = process_timer()
    all_users = collect_users(num_files)
    tot_users = len(all_users)
    
    num_files_needed = (tot_users // STATS_PAGE_LEN)
    
    if num_files_needed * STATS_PAGE_LEN < tot_users: num_files_needed += 1
    
    start_idx = 0
    for pg in range(num_files_needed):
        end_idx = start_idx + STATS_PAGE_LEN
        
        page_data = {
            uid: stats for uid, stats in all_users[start_idx:end_idx]
        }
        page_path = f"user_data/stats/{pg}"
        savejson(page_path, page_data)
        
        start_idx = end_idx
    
    savejson("user_data/stats/file_ct", [num_files_needed])
    timer.end(f"Sorted stats for {tot_users} users")

def sort_in_file(filepath: str, data: dict = None):
    if data == None:
        data = loadjson(filepath)
    
    sorted_data = {uid: data[uid] for uid in sorted(data.keys())}
    savejson(filepath, sorted_data)

def add_user(user_id: int, num_files: int, stats: dict = None):
    user_stats = search_stats_files(user_id, num_files)
    
    stats = stats if stats else DEFAULT_STATS
    
    if user_stats == None: 
        user_stats = stats
    else:
        return
    
    left = 0
    right = num_files - 1
    target_fp = f"user_data/stats/{num_files - 1}"
    
    while left <= right:
        mid = (left + right) // 2
        mid_fp = f"user_data/stats/{mid}"
        mid_file = load_file_for_search(mid_fp)
        
        first_id = int(mid_file[0][0])
        last_id = int(mid_file[0][0])
        
        if first_id <= user_id <= last_id:
            target_fp = mid_fp
            break
        elif user_id < first_id:
            right = mid - 1
        
        else:
            left = mid + 1
    
    target_page = loadjson(target_fp)
    target_page.update({user_id: user_stats})
    sort_in_file(target_fp, target_page)
    
    if len(target_page.keys()) >= STATS_PAGE_LEN:
        sort_stats(num_files)

def update_user(user_id: int, new_stats: dict, num_files: int):
    left = 0
    right = num_files - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_fp = f"user_data/stats/{mid}"
        mid_file = loadjson(mid_fp)
        
        if not mid_file:
            if left == right:
                break
            left = mid + 1
            continue
        
        user_ids = sorted(mid_file.keys())
        if user_id in user_ids:
            mid_file[user_id].update(new_stats)
            savejson(mid_fp, mid_file)
            return True
        
        elif user_id < user_ids[0]:
            right = mid - 1
        
        else:
            left = mid + 1
    
    return False

def fetch_file_ct():
    num_files = loadjson("user_data/stats/file_ct")[0]
    return num_files

def collect_vals(value: str, sorted: bool = True):
    """
    ### Values:
    
    **'stars_recieved'** - The number of stars given to a user on messages sent to the star board
    
    **'board_msgs'** - The number of the user's messages sent to the star board
    
    **'fish_caught'** - The number of fish caught by the user
    
    **'times_pondered'** - The number of times the /ponder command was used
    """
    if value not in VALID_VALS: return
    num_files = fetch_file_ct()
    all_users = collect_users(num_files)
    all_values = []
    
    for uid, stats in all_users:
        target = stats.get(value)
        if not target or target == 0: continue
        all_values.append((uid, target))
    
    if sorted:
        all_values.sort(key=lambda x: x[0])
    
    return all_values

def get_value_choices():
    choices = []
    for val in VALID_VALS:
        name = val.replace("_", " ").title()
        choices.append(app_commands.Choice(name=name, value=val))
    return choices

class userstats():
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.valid_vals = VALID_VALS
    
    def get_stats(self):
        user_stats = search_stats_files(self.user_id, fetch_file_ct())
        
        if user_stats == None:
            return DEFAULT_STATS
        
        return user_stats
    
    def update_stats(self, user_stats: dict):
        updated = update_user(self.user_id, user_stats, fetch_file_ct())
        
        if not updated:
            add_user(self.user_id, fetch_file_ct(), user_stats)
    
    def get_value(self, value: str):
        """
        ### Values:
        
        **'stars_recieved'** - The number of stars given to a user on messages sent to the star board
        
        **'board_msgs'** - The number of the user's messages sent to the star board
        
        **'fish_caught'** - The number of fish caught by the user
        
        **'times_pondered'** - The number of times the /ponder command was used
        """
        if value not in self.valid_vals: return
        user_stats = self.get_stats()
        value = user_stats.setdefault(value, 0)
        return value
    
    def update_value(self, value: str, set: int = None, change: int = 0):
        """
        ### Values:
        
        **'stars_recieved'** - The number of stars given to a user on messages sent to the star board
        
        **'board_msgs'** - The number of the user's messages sent to the star board
        
        **'fish_caught'** - The number of fish caught by the user
        
        **'times_pondered'** - The number of times the /ponder command was used
        """
        if value not in self.valid_vals: return
        
        user_stats = self.get_stats()
        total = user_stats.setdefault(value, 0) + change
        
        if set:
            total = set + change
        
        user_stats.update({value: total})
        self.update_stats(user_stats)
    
    def to_string(self):
        user_stats = self.get_stats()
        stats_str = ""
        
        for label in user_stats.keys():
            value = user_stats.get(label)
            label = label.replace("_", " ").title()
            stats_str += f"{label}: {value}\n"
        
        return stats_str
    
    @classmethod
    def from_discord_user(cls, user: discord.User):
        return cls(user.id)
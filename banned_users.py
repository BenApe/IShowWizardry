from botutils import loadjson, savejson, get_discord_timestamp
from datetime import datetime, timedelta

class BannedUsers():
    def __init__(self):
        self.banned_users_path = "bot_data/banned_users"
        self.banned_users = loadjson(file_name=self.banned_users_path)
        self.default_ban_length = 168 # hours (1 week)
    
    def update_user(self, user_id:int, offenses:int = None):
        now = datetime.now().isoformat()
        
        if user_id not in self.banned_users:
            self.banned_users.update({user_id: {"offenses": 1, "last_offense": now}})
            savejson(self.banned_users_path, self.banned_users)
            return self.banned_users.get(user_id)
        
        user_data = self.banned_users.get(user_id)
        offense_ct = user_data.get("offenses")
        offense_ct += offenses or 1
        user_data.update({"offenses": offense_ct, "last_offense": now})
        self.banned_users.update(user_data)
        savejson(self.banned_users_path, self.banned_users)
        return self.banned_users
    
    def remove_user(self, user_id:int):
        user = self.banned_users.pop(user_id)
        savejson(self.banned_users_path, self.banned_users)
        return user
    
    def check_user(self, user_id:int):
        if user_id in self.banned_users:
            user_data = self.banned_users.get(user_id)
            offenses = user_data.get("offenses")
            
            if offenses == 0:
                return False
            
            last_offense = datetime.fromisoformat(user_data.get("last_offense"))
            now = datetime.now()
            
            if now - last_offense > timedelta(hours=self.default_ban_length):
                return False
        
        else:
            return False
        
        return True
    
    def get_timestamp(self, user_id:int):
        if user_id not in self.banned_users:
            return None
        
        user_data = self.banned_users.get(user_id)
        last_offense = datetime.fromisoformat(user_data.get("last_offense"))
        end_time = last_offense + timedelta(hours=self.default_ban_length)
        timestamp = get_discord_timestamp(iso_time=end_time.isoformat(), style='f')
        
        return timestamp
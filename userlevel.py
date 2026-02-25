import math

from botutils import savejson, loadjson

class userlevel():
    def __init__(self, user_id:int, server_id:int):
        self.user_id = user_id
        self.server_id = server_id
        self.levels_path = f"user_data/levels/{server_id}"
        self.default_data = {self.user_id: {"xp": 0, "level": 0}}
    
    def get_level(self):
        server_level_data = loadjson(self.levels_path)
        
        if not server_level_data.get(self.user_id):
            server_level_data.update(self.default_data)
            savejson(self.levels_path, server_level_data)
            return 1
        
        user_level_data = server_level_data.get(self.user_id)
        return user_level_data.get("level")
    
    def get_xp(self):
        server_level_data = loadjson(self.levels_path)
        
        if not server_level_data.get(self.user_id):
            server_level_data.update(self.default_data)
            savejson(self.levels_path, server_level_data)
            return 0
        
        user_level_data = server_level_data.get(self.user_id)
        return user_level_data.get("xp")
    
    def get_user_data(self):
        server_level_data = loadjson(self.levels_path)
        
        if not server_level_data.get(self.user_id):
            server_level_data.update(self.default_data)
            savejson(self.levels_path, server_level_data)
        
        return server_level_data.get(self.user_id)
    
    def set_user_data(self, user_data:dict):
        server_level_data = loadjson(self.levels_path)
        server_level_data.update(user_data)
        savejson(self.levels_path, server_level_data)
        return server_level_data
    
    def check_level(self):
        user_data = self.get_user_data()
        user_xp = user_data.get("xp")
        user_level = xp_to_lvl(user_xp)
        
        if user_data.get("level") != user_level:
            self.set_user_data({self.user_id: {"xp": user_xp, "level": user_level}})
        
        return user_level
    
    def xp_required(self, level:int = None):
        if level == None:
            level = self.get_level()
        
        return lvl_to_xp(level=level)
    
    def progressbar(self):
        user_data = self.get_user_data()
        user_level = user_data.get("level")
        user_xp = user_data.get("xp")
        
        if user_xp == 0:
            return f"{user_level} ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ {user_level + 1}"
        
        progress_chunks = int(((user_xp + 10 - self.xp_required()) / (self.xp_required() - self.xp_required(user_level - 1))) * 10)
        
        bar = f"{user_level} "
        
        for i in range(progress_chunks):
            bar += "🟩"
        
        for i in range(10 - progress_chunks):
            bar += "⬛"
        
        bar += f" {user_level + 1}"
        
        return bar
    
    def add_xp(self, amount:int):
        user_data = self.get_user_data()
        xp = user_data.get("xp") + amount
        self.set_user_data({self.user_id: {"xp": xp, "level": user_data.get('level')}})
        self.check_level()
        return xp

def lvl_to_xp(level:int):
    if level < 6:
        return 10 * level + 15
    
    elif level < 11:
        return 25 * level - 60
    
    else:
        b = 10 - math.log(x=190)
        return math.exp(x=level - b)

def xp_to_lvl(xp:int):
    cap_0 = 15
    cap_1 = 65
    cap_2 = 190
    
    if xp <= cap_0:
        return 0
    
    elif xp <= cap_1:
        return int((xp - 15) / 10) + 1
    
    elif xp <= cap_2:
        return int((xp + 60) / 25) + 1
    
    else:
        return int(math.log(xp / cap_2) + 10) + 1
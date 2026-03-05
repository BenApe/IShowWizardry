from bot_data.bannedwordlist import words

class BannedWords():
    def __init__(self, tier1:bool = True, tier2:bool = True, tier3:bool = True, tier4:bool = True):
        self.custom_list = words
        self.blacklist = {}
        self.enabled_tiers = {
            1: tier1,
            2: tier2,
            3: tier3,
            4: tier4
        }
        
    def get_current_list(self):
        return self.custom_list
    
    def disable_tier(self, tier:int):
        self.enabled_tiers[tier] = False
        return self.enabled_tiers
        
    def enable_tier(self, tier:int):
        self.enabled_tiers[tier] = True
        return self.enabled_tiers
    
    def add_word(self, word:str, tier:int):
        self.custom_list.update({word: tier})
        self.blacklist.pop(word)
        return self.custom_list
    
    def remove_word(self, word:str):
        self.custom_list.pop(word)
        self.blacklist.update(word)
        return self.custom_list
    
    def isprofane(self, word:str):
        if self.blacklist.get(word):
            return False
        
        tier = self.custom_list.get(word)
        
        if not tier:
            return False
        
        if not self.enabled_tiers.get(tier):
            return False
        
        return True
import discord
import random

from botutils import break_lines

class spell():
    def __init__(self, owner:discord.User, name:str = "", spell_type:str = "", rarity:str = "", damage_min:int = 0, damage_max:int = 0, shield:int = 0, heal:int = 0, damage_boost:int = 0, uses:int = 0, description:str=""):
        self.name = name
        self.owner = owner
        self.spell_type = spell_type
        self.rarity = rarity
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.shield = shield
        self.heal = heal
        self.damage_boost = damage_boost
        self.uses = uses
        self.description = description
    
    def get_name(self):
        return self.name
    
    def set_name(self, name:str):
        self.name = name
        return name
    
    def get_owner(self):
        return self.owner
    
    def set_owner(self, owner:discord.User):
        self.owner = owner
        return owner
    
    def get_spell_type(self):
        return self.spell_type
    
    def set_spell_type(self, spell_type:str):
        self.spell_type = spell_type
        return spell_type
    
    def get_damage(self):
        return self.damage_min, self.damage_max
    
    def set_damage(self, damage_min:int = None, damage_max:int = None):
        if damage_min != None:
            self.damage_min = damage_min

        if damage_max != None:
            self.damage_max = damage_max
        
        return self.damage_min, self.damage_max
    
    def get_shield(self):
        return self.shield
    
    def set_shield(self, shield:int):
        self.shield = shield
        return shield
    
    def get_heal(self):
        return self.heal
    
    def set_heal(self, heal:int):
        self.heal = heal
        return heal
    
    def get_damage_boost(self):
        return self.damage_boost
    
    def set_damage_boots(self, damage_boost:int):
        self.damage_boost = damage_boost
        return damage_boost
    
    def get_uses(self):
        return self.uses
    
    def set_uses(self, uses:int):
        self.uses = uses
        return uses
    
    def calc_damage(self):
        return random.randint(self.damage_min, self.damage_max)
    
    def use(self):
        self.uses -= 1 if self.uses > 0 else 0
        
        return self.uses
    
    def to_dict(self):
        spell_dict = {
            "name": self.name,
            "type": self.type,
            "rarity": self.rarity,
            "damage_min": self.damage_min,
            "damage_max": self.damage_max,
            "shield": self.shield,
            "heal": self.heal,
            "damage_boost": self.damage_boost,
            "uses": self.uses,
            "description": self.description
        }
        
        return spell_dict
        
    def from_dict(self, dict:dict):
        self.name = dict.get("name")
        self.type = dict.get("type")
        self.rarity = dict.get("rarity")
        self.damage_min = dict.get("damage_min")
        self.damage_max = dict.get("damage_max")
        self.shield = dict.get("shield")
        self.heal = dict.get("heal")
        self.damage_boost = dict.get("damage_boost")
        self.uses = dict.get("uses")
        self.description = dict.get("description")
        
        return self
    
    def to_string(self):
        top =       "┌──────────────────┐\n"
        seperator = "│──────────────────│\n"
        blank =     "│                  │\n"
        bottom =    "└──────────────────┘"
        linelen = len(top)
        
        spell_data = self.to_dict().items()
        
        spell_card = top
        
        for item in spell_data:
            label = str(item[0])
            info = str(item[1])
            line = ""
            
            if str(info) == "0" or label == "damage_min" or label == "rarity":
                continue
            
            if label == "name":
                line = f"│{info}"
                
            elif label == "type":
                line = f"│{info} Spell"
            
            elif label == "damage_max":
                line = f"│Damage: {self.damage_min}-{info}"
                
            elif label == "description":
                info += f" ({self.rarity})."
                lines = break_lines(text=info, max_len=linelen - 3)
                description = blank
                
                for item in lines:
                    if len(item) < linelen:
                        for i in range(linelen - 3 - len(item)):
                            item += " "
                    
                    description += f"│{item}│\n"
                
                spell_card += description
                continue
            
            else:
                label = label.replace("_", " ").capitalize()
                line = f"│{label}: {info}"
            
            if len(line) < linelen:
                for i in range(linelen - 2 - len(line)):
                    line += " "

            spell_card += f"{line}│\n"
            
            if label == "name":
                spell_card += seperator
                
            elif label == "type":
                spell_card += blank
        
        return spell_card + bottom
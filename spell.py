import discord
import random

class spell():
    def __init__(self, name:str, owner:discord.User, spell_type:str, damage_min:int = 0, damage_max:int = 0, shield:int = 0, heal:int = 0, damage_boost:int = 0, uses:int = 0):
        self.name = name
        self.owner = owner
        self.spell_type = spell_type
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.shield = shield
        self.heal = heal
        self.damage_boost = damage_boost
        self.uses = uses
    
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
        return random.randint(self.damage_min, self.damage_max) + self.damage_boost
    
    def use(self):
        self.uses -= 1 if self.uses > 0 else 0
        
        return self.uses
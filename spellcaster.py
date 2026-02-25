import spell
import discord
import random

class spellcaster():
    def __init__(self, user:discord.User, health:int = 40, max_health:int=40):
        self.user = user
        self.health = health
        self.max_health = max_health
        self.shield = 0
        self.damage_boost = 0
        self.cast_this_turn = []
    
    def get_user(self):
        return self.user
    
    def set_user(self, user:discord.User):
        self.user = user
        return user
    
    def get_health(self):
        return self.health
    
    def set_health(self, health:int):
        self.health = health
        return health
    
    def get_shield(self):
        return self.shield
    
    def set_shield(self, shield:int):
        self.shield = shield
        return shield
    
    def get_damage_boost(self):
        return self.damage_boost
    
    def set_damage_boost(self, damage_boost:int):
        self.damage_boost = damage_boost
        return damage_boost
    
    def heal(self, amount:int):
        self.health += amount
        
        if self.health > self.max_health:
            self.health = self.max_health
        
        return self.health
    
    def hurt(self, amount:int, ignore_shield:bool = False):
        if not ignore_shield:
            if amount >= self.shield:
                amount -= self.shield
                self.shield = 0
            
            else:
                self.shield -= amount
                return self.health
                
        self.health -= amount
        return self.health
    
    def add_shield(self, amount:int):
        self.shield += amount
        
        return self.shield
    
    def cast_spell(self, spell_type:str):
        self.cast_this_turn.append(spell_type)
        
        return self.cast_this_turn
    
    def next_turn(self):
        self.cast_this_turn = []
    
    def to_string(self):
        casted = ""
        
        for item in self.cast_this_turn:
            casted += item
        
        caster = f"**Health:** {self.health}/{self.max_health}\n**Shield:** {self.shield}\n**Damage Boost:** {self.damage_boost}\n**Casted This Turn:** {casted}"
        
        return caster
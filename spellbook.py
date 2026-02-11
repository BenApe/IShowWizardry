import discord
import spell

class spellbook():
    def __init__(self, owner:discord.User):
        self.owner = owner
        
        self.default_spellbook = {
            0: {
                "name": "Fireball",
                "type": "Attack",
                "rarity": "Common",
                "damage_min": 5,
                "damage_max": 15,
                "shield": 0,
                "heal": 0,
                "damage_boost": 0,
                "uses": 4,
                "description": "Basic attack spell"
            },
            1: {
                "name": "Lightning",
                "type": "Special",
                "rarity": "Common",
                "damage_min": 0,
                "damage_max": 8,
                "shield": 0,
                "heal": 0,
                "damage_boost": 0,
                "uses": 3,
                "description": "Ignores shields when dealing damage"
            },
            2: {
                "name": "Regenerate",
                "type": "Healing",
                "rarity": "Common",
                "damage_min": 0,
                "damage_max": 0,
                "shield": 0,
                "heal": 30,
                "damage_boost": 0,
                "uses": 1,
                "description": "Basic healing spell"
            },
            3: {
                "name": "Wizard Shield",
                "type": "Shield",
                "rarity": "Common",
                "damage_min": 0,
                "damage_max": 0,
                "shield": 15,
                "heal": 0,
                "damage_boost": 0,
                "uses": 3,
                "description": "Basic shield spell"
            }
        }
    
    def get_spells(self, as_dict:bool = True):
        user_spellbook = self.default_spellbook
        
        if as_dict: 
            return user_spellbook
        
        return spell_dict_to_list(dict=user_spellbook, owner=self.owner)

    def get_prepared_spells(self, as_dict:bool = True):
        user_spellbook = self.default_spellbook
        
        if as_dict: 
            return user_spellbook
        
        return spell_dict_to_list(dict=user_spellbook, owner=self.owner)
    
    def prepared_spells_to_string(self):
        prepared_spells = self.default_spellbook
        
        spell_list = spell_dict_to_list(dict=prepared_spells, owner=self.owner)
        
        for item in spell_list:
            user_spell = item.to_string()
            lines = user_spell.split("\n")
            
        pass

def spell_dict_to_list(dict:dict, owner:discord.User):
    spell_list = []
    
    for item in dict:
        user_spell = spell.spell(owner=owner)
        user_spell.from_dict(dict.get(item))
        spell_list.append(user_spell)
    
    return spell_list
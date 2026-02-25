import discord
import spellcaster
import spellbook
import spell
import random

class gamemaster():
    def __init__(self, player1:spellcaster.spellcaster, player2:spellcaster.spellcaster):
        self.player1 = player1
        self.player2 = player2
        self.playing = False
        self.turn = 0
    
    def start_game(self):
        self.playing = True
        self.turn = random.randint(0, 1)
        
        return self.get_turn().get_user()
        
    def get_turn(self):
        if self.turn % 2 == 0:
            return self.player1
        
        return self.player2
    
    def next_turn(self):
        self.get_turn().next_turn()
        self.turn += 1
        
        return self.get_turn()
    
    def cast_spell(self, caster:spellcaster.spellcaster, casted:spell.spell):
        opponent = self.player1 if self.player1 != caster else self.player2
        caster.cast_spell(casted.get_spell_type())
        
        if casted.get_spell_type() == "Attack":
            damage_boost = caster.get_damage_boost()
            damage = casted.calc_damage() + damage_boost
            opponent.hurt(damage)
            
            return {"damage": damage, "target": opponent.get_user().id}
        
        elif casted.get_spell_type() == "Shield":
            shield = casted.get_shield()
            caster.add_shield(shield)
            
            return {"shield": shield, "target": caster.get_user().id}
        
        elif casted.get_spell_type() == "Healing":
            healing = casted.get_heal()
            caster.heal(healing)
            
            return {"heal": healing, "target": caster.get_user().id}
        
        else:
            pass
    
    def special_spells(self, casted: spell.spell):
        pass
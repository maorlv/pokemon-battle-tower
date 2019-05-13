import random
from numpy.random import choice as npchoice
import p_types

class Move:
    def __init__(self, name, a_type, power, pp, accuracy, priority, targetOpponent = True):
        self.name = name
        self.power = power
        self.a_type = a_type
        self.pp = pp
        self.accuracy = accuracy
        self.priority = priority
        self.targetOpponent = targetOpponent
        self.messages = []

    def getPP(self):
        return self.pp

    def getType(self):
        return self.a_type

    def getPower(self):
        return self.power

    def getName(self):
        return self.name

    def getPriority(self):
        return self.priority
    
    def getAccuracy(self):
        return self.accuracy
    
    def getCategory(self):
        raise NotImplementedError

    def opponentImmune(self, opponentTypes):
        for op_type in opponentTypes:
            if self.a_type in op_type.getImmunities():
                return True
        return False
    
    def accuracyCheck(self, user, opponent):
        # Move's target is the opponent, so check if it's immune to the attack
        if self.opponentImmune(opponent.getTypes()) and self.targetOpponent:
            self.messages.append(" - But it failed...")
            return False

        # Not immune/Not attacking opponent, check accuracy
        accuracy_check = npchoice([True, False], 1, p = [self.accuracy, 1-self.accuracy])
        if accuracy_check == False:
            self.messages.append(" - But it missed!")
            return False
        
        return True

    def modifier(self, userTypes, opponentTypes, in_battle = True):
        type_factor = 1
        for op_type in opponentTypes:
            if self.a_type in op_type.getResistance():
                type_factor *= 0.5
            if op_type in self.a_type.getSuperEffective():
                type_factor *= 2

        if type_factor >= 2 and in_battle:
            self.messages.append(" - It's super effective!")
        elif type_factor < 1 and in_battle:
            self.messages.append(" - It's not very effective...")

        stab = 1.5 if self.a_type in userTypes else 1

        rand = random.uniform(0.85, 1) if in_battle else 1
        return type_factor * stab * rand

    def use(self, user, opponent):
        # initialize messages with "{Enemy }user.name used move.name"
        self.messages = ["{}{} used {}!".format("Enemy " if user.isEnemy() else "", user.getName(), self.name)]

        if self.accuracyCheck(user, opponent):
            modifier = self.modifier(user.getTypes(), opponent.getTypes()) if self.targetOpponent else 0
            damage = self.effect(user, opponent, modifier)
            damage = self.additionalEffect(user, opponent, damage)
            opponent.decreaseHP(damage)

            for pkmn in [user, opponent]:
                if pkmn.getHP() == 0:
                    self.messages.append("{}{} fainted!".format("Enemy " if pkmn.isEnemy() else "", pkmn.getName()))
        
        self.pp -= 1
        return self.messages

    def calculateDamage(self, level, atkState, defState, modifier):
        damage = ((2*level/5 + 2) * self.power * (atkState/defState))/50 + 2
        return int(damage * modifier)

    def effect(self, user, opponent, modifier):
        raise NotImplementedError

    def additionalEffect(self, user, opponent, damage):
        return damage

    def recoil(self, user, damage):
        user.decreaseHP(damage)
        self.messages.append("{} is damaged by recoil!".format(user.getName()))

    def heal(self, user, hp):
        gained = user.increaseHP(hp)
        if gained > 0:
            self.messages.append(" - {}'s HP was restored.".format(self.name))
        else:
            self.messages.append(" - {}'s HP was already full...".format(self.name))

    def multiStrike(self, max_s):
        num_of_hits = 2
        if max_s == 5:
            num_of_hits = random.choices([2,3,4,5], [1/3, 1/3, 1/6, 1/6], k=1)[0]
        self.messages.append(" - Hit {} times!".format(num_of_hits))
        
        return num_of_hits

    def heuristicValue(self, user, opponent, rand_mode):
        rand_effect = {"avg": 0.925, "max": 1, "min": 0.85}
        accuracy_effect = self.getAccuracy() if rand_mode == "avg" else 1

        # average modifier and damage
        h_val = 0
        if not self.opponentImmune(opponent.getTypes()):
            modifier = self.modifier(user.getTypes(), opponent.getTypes(), False) * rand_effect[rand_mode]
            h_val = self.effect(user, opponent, modifier) * accuracy_effect

        return [h_val, 0]

class SpecialMove(Move):
    def effect(self, user, opponent, modifier):
        damage = self.calculateDamage(user.getLevel(), user.getSpAtk(), opponent.getSpDef(), modifier)
        return damage

    def getCategory(self):
        return "Special"

class PhysicalMove(Move):
    def effect(self, user, opponent, modifier):
        damage = self.calculateDamage(user.getLevel(), user.getAtk(), opponent.getDef(), modifier)
        return damage

    def getCategory(self):
        return "Physical"

class StatusMove(Move):
    def effect(self, user, opponent, modifier):
        return 0

    def getCategory(self):
        return "Status"

""" 
=========================
=   MOVE DEFINITIONS:   =
=========================
"""

class Flamethrower(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Flamethrower", p_types.FIRE, 90, 15, 1, 0)

class Venoshock(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Venoshock", p_types.POISON, 65, 10, 1, 0)

class SlugdeBomb(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Slugde Bomb", p_types.POISON, 90, 10, 1, 0)

class Struggle(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Struggle", p_types.NOTYPE, 50, float('Inf'), 1, 0)
    
    def additionalEffect(self, user, opponent, damage):
        self.recoil(user, int(user.getMaxHP()/4))
        return damage
        
class Thunderbolt(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Thunderbolt", p_types.ELECTRIC, 90, 15, 1, 0)

class Surf(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Surf", p_types.WATER, 90, 15, 1, 0)

class WaterPulse(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Water Pulse", p_types.WATER, 60, 20, 1, 0)

class IceBeam(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Ice Beam", p_types.ICE, 90, 15, 1, 0)

class Psychic(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Psychic", p_types.PSYCHIC, 90, 15, 1, 0)

class Psybeam(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Psybeam", p_types.PSYCHIC, 65, 20, 1, 0)

class EnergyBall(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Energy Ball", p_types.GRASS, 90, 15, 1, 0)

class Earthquake(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Earthquake", p_types.GROUND, 100, 10, 1, 0)

class DrillRun(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Drill Run", p_types.GROUND, 80, 10, 0.95, 0)

class XScissor(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "X-Scissor", p_types.BUG, 80, 15, 1, 0)

class RockSlide(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Rock Slide", p_types.ROCK, 75, 10, 0.9, 0)

class Bulldoze(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Bulldoze", p_types.GROUND, 60, 20, 1, 0)

class IcyWind(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Icy Wind", p_types.ICE, 55, 15, 0.95, 0)

class AirSlash(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Air Slash", p_types.FLYING, 75, 20, 0.95, 0)

class WingAttack(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Wing Attack", p_types.FLYING, 60, 35, 1, 0)

class SignalBeam(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Signal Beam", p_types.BUG, 75, 15, 1, 0)

class Slash(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Slash", p_types.NORMAL, 70, 20, 1, 0)

class Headbutt(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Headbutt", p_types.NORMAL, 70, 15, 1, 0)

class Strength(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Strength", p_types.NORMAL, 80, 15, 1, 0)

class QuickAttack(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Quick Attack", p_types.NORMAL, 40, 30, 1, 1)
    
class BulletPunch(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Bullet Punch", p_types.STEEL, 40, 30, 1, 1)

class Bite(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Bite", p_types.DARK, 60, 25, 1, 0)

class ThunderFang(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Thunder Fang", p_types.ELECTRIC, 65, 15, 0.95, 0)

class ShadowBall(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Shadow Ball", p_types.GHOST, 80, 15, 1, 0)

class DazzlingGleam(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Dazzling Gleam", p_types.FAIRY, 80, 10, 1, 0)

class Moonblast(SpecialMove):
    def __init__(self):
        Move.__init__(self, "Moonblast", p_types.FAIRY, 95, 15, 1, 0)

class TakeDown(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Take Down", p_types.NORMAL, 90, 20, 0.85, 0)

    def additionalEffect(self, user, opponent, damage):
        self.recoil(user, int(damage/4))
        return damage

class BrickBreak(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Brick Break", p_types.FIGHTING, 75, 15, 1, 0)

class IcePunch(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Ice Punch", p_types.ICE, 75, 15, 1, 0)

class Recover(StatusMove):
    def __init__(self):
        Move.__init__(self, "Recover", p_types.NORMAL, 0, 10, 1, 0, False)
    
    def additionalEffect(self, user, opponent, modifier):
        self.heal(user, int(user.getMaxHP()/2))
        return 0

    def heuristicValue(self, user, opponent, rand_mode):
        return [0, -int(user.getMaxHP()/2)]

class IronTail(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Iron Tail", p_types.STEEL, 100, 15, 0.75, 0)

class FoulPlay(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Foul Play", p_types.DARK, 95, 15, 1, 0)

class DoubleKick(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Double Kick", p_types.FIGHTING, 30, 30, 1, 0)
    
    def additionalEffect(self, user, opponent, damage):
        return damage * self.multiStrike(2)

    def heuristicValue(self, user, opponent, rand_mode):
        return Move.heuristicValue(self, user, opponent, rand_mode) * 2

class PinMissile(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Pin Missile", p_types.BUG, 30, 30, 0.95, 0)
    
    def additionalEffect(self, user, opponent, damage):
        return damage * self.multiStrike(5)
    
    def heuristicValue(self, user, opponent, rand_mode):
        return [Move.heuristicValue(self, user, opponent, rand_mode)[0] * 19 / 6, 0]

class BulletSeed(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Bullet Seed", p_types.GRASS, 25, 30, 1, 0)
    
    def additionalEffect(self, user, opponent, damage):
        return damage * self.multiStrike(5)

class AerialAce(PhysicalMove):
    def __init__(self):
        Move.__init__(self, "Aerial Ace", p_types.FLYING, 60, 20, 1, 0)
    

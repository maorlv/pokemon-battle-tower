import random
import p_types
import moves

class Pokemon:
    def __init__(self, name, base_stats, types, p_moves, level = 50):
        self.name = name
        self.level = level
        self.types = types
        self.moves = [move() for move in p_moves]
        self.is_enemy = True
        self.stats = []
        self.hp = 0
        self.calculateRandomStats(base_stats)
        #self.status = ""
        #self.confused = False

    def calculateRandomStats(self, base_stats):
        ivs = [random.randint(0, 31) for i in range(6)]

        evs = []
        max_evs_left = 508
        for i in range(6):
            evs.append( random.randint(0, min(252, max_evs_left)) )
            max_evs_left -= evs[i]

        # sort evs randomly so every stat will get an even chance to be increased
        def sortRandom(k):
            return random.random()
        evs.sort(key = sortRandom)
        
        # nature may not affect HP
        nature_up = random.randint(1,5)
        nature_down = random.randint(1,5)
        nature_effect = [1 for i in range(6)]
        if nature_down != nature_up:
            nature_effect[nature_up] = 1.1
            nature_effect[nature_down] = 0.9

        def stat_calculate_shared(i):
            return int( (2*base_stats[i] + ivs[i] + int(evs[i]/4)) * self.level / 100 )
        
        hp = stat_calculate_shared(0) + self.level + 10
        self.stats.append(hp)
        self.hp = hp

        for i in range(1,6):
            stat = int( (stat_calculate_shared(i) + 5) * nature_effect[i] )
            self.stats.append(stat)

    def setPlayer(self):
        self.is_enemy = False

    def isEnemy(self):
        return self.is_enemy

    def getName(self):
        return self.name

    def getMoves(self):
        legalMoves = []
        for move in self.moves:
            if move.getPP() > 0:
                legalMoves.append(move)
        
        if len(legalMoves) == 0:
            struggle = moves.Struggle()
            self.moves = [struggle]
            legalMoves = [struggle]
        
        return legalMoves

    def getTypes(self):
        return self.types

    def getLevel(self):
        return self.level

    def getHP(self):
        return self.hp
    
    def getMaxHP(self):
        return self.stats[0]

    def getHPPercentage(self):
        return min(int(self.hp * 100 / self.stats[0]) + 1, 100)

    def getAtk(self):
        return self.stats[1]

    def getDef(self):
        return self.stats[2]

    def getSpAtk(self):
        return self.stats[3]

    def getSpDef(self):
        return self.stats[4]

    def getSpeed(self):
        return self.stats[5]

    def decreaseHP(self, damage):
        lose = min(damage, self.hp)
        self.hp -= lose
        return lose            
    
    def increaseHP(self, hp):
        gain = min(hp, self.getMaxHP() - self.hp)
        self.hp += gain
        return gain
            
    def printStats(self):
        return """{}'s stats:
HP: {}, Atk: {}, Def: {}, SpAtk: {}, SpDef: {}, Speed: {}""".format(self.name, self.stats[0], self.stats[1], self.stats[2], self.stats[3], self.stats[4], self.stats[5])

""" 
=============================================
=   POKEMON SELECTION HEURISTIC FUNCTION:   =
=============================================
"""
pokemonShell = Pokemon("shell", [0 for i in range(6)], [], [])

def updateShell(m):
    pokemonShell.moves = [move() for move in PokemonList[m]['moves']]
    pokemonShell.types = PokemonList[m]['types']
    avg_iv_bonus = 31/2
    some_ev_bonus = 10 # will usually be more than that...
    avg_stat_bonus = some_ev_bonus + avg_iv_bonus
    # not true for hp, but who cares:
    avg_stats = [(2*stat + avg_stat_bonus)*pokemonShell.getLevel()/100 + 5 for stat in PokemonList[m]['base_stats']]
    pokemonShell.stats = avg_stats

def heuristicAux(attacker, defender):
    cur_h = 0
    for move in attacker.getMoves():
        move_h = move.heuristicValue(attacker, defender, "avg")[0]
        cur_h = max(cur_h, move_h)

    return cur_h

# returns the potential to do more damage to the player's partners
def heuristicValue(m, rival, others):
    h = 0
    other_len = len(others) - 1
    # get the m-pokemon into the shell with average stats
    updateShell(m)
    for opponent in others:
        def_h = heuristicAux(opponent, pokemonShell)
        atk_h = heuristicAux(pokemonShell, opponent)

        # faster pokemon might ko the other
        if pokemonShell.getSpeed() > opponent.getSpeed():
            atk_h *= 1.5
        elif pokemonShell.getSpeed() < opponent.getSpeed():
            def_h *= 1.5

        cur_h = atk_h - def_h
        h += cur_h if opponent == rival else cur_h/(3*other_len)

    return h

""" 
=============================
=   POKEMONS DEFINITIONS:   =
=============================
"""
import numpy as np
def sortByName(elm):
    return elm[0]
pklist = []
pklist.append(("Charizard", [78, 84, 78, 109, 85, 100], [p_types.FIRE, p_types.FLYING], [moves.Flamethrower, moves.AirSlash, moves.Slash, moves.Earthquake]))
pklist.append(("Houndoom", [75, 90, 50, 110, 80, 95], [p_types.DARK, p_types.FIRE], [moves.Flamethrower, moves.Bite, moves.ThunderFang, moves.ShadowBall]))
pklist.append(("Raichu", [60, 90, 55, 90, 80, 110], [p_types.ELECTRIC], [moves.Thunderbolt, moves.QuickAttack, moves.Strength, moves.SignalBeam]))
pklist.append(("Ampharos", [90, 75, 85, 115, 90, 55], [p_types.ELECTRIC], [moves.Thunderbolt, moves.TakeDown, moves.BrickBreak, moves.SignalBeam]))
pklist.append(("Blastoise", [79, 83, 100, 85, 105, 78], [p_types.WATER], [moves.Surf, moves.IcyWind, moves.Earthquake, moves.Headbutt]))
pklist.append(("Lapras", [130, 85, 80, 85, 95, 60], [p_types.WATER, p_types.ICE], [moves.IceBeam, moves.WaterPulse, moves.Headbutt, moves.DrillRun]))
pklist.append(("Venusaur", [80, 82, 83, 100, 100, 80], [p_types.GRASS, p_types.POISON], [moves.EnergyBall, moves.Venoshock, moves.Earthquake, moves.Headbutt]))
pklist.append(("Exeggutor", [80, 82, 83, 100, 100, 80], [p_types.GRASS, p_types.PSYCHIC], [moves.EnergyBall, moves.Psybeam, moves.Headbutt, moves.SlugdeBomb]))
pklist.append(("Tauros", [75, 100, 95, 40, 70, 110], [p_types.NORMAL], [moves.TakeDown, moves.Surf, moves.Earthquake, moves.Flamethrower]))
pklist.append(("Alakazam", [55, 50, 45, 135, 95, 120], [p_types.PSYCHIC], [moves.Psychic, moves.DazzlingGleam, moves.Recover, moves.IcePunch]))
pklist.append(("Scizor", [70, 130, 100, 55, 80, 65], [p_types.BUG, p_types.STEEL], [moves.BulletPunch, moves.XScissor, moves.Slash, moves.BrickBreak]))
pklist.append(("Heracross", [80, 125, 75, 40, 95, 85], [p_types.BUG, p_types.FIGHTING], [moves.AerialAce, moves.PinMissile, moves.BulletSeed, moves.BrickBreak]))
pklist.append(("Clefable", [95, 70, 73, 95, 90, 60], [p_types.FAIRY], [moves.BrickBreak, moves.Moonblast, moves.ShadowBall, moves.IcePunch]))
pklist.append(("Machamp", [90, 130, 80, 65, 85, 55], [p_types.FIGHTING], [moves.BulletPunch, moves.Flamethrower, moves.BrickBreak, moves.Earthquake]))
pklist.append(("Dragonite", [91, 134, 95, 100, 100, 80], [p_types.DRAGON, p_types.FLYING], [moves.WingAttack, moves.Flamethrower, moves.Thunderbolt, moves.IcePunch]))
pklist.append(("Gengar", [60, 65, 60, 130, 75, 110], [p_types.GHOST, p_types.POISON], [moves.ShadowBall, moves.Venoshock, moves.DazzlingGleam, moves.IcePunch]))
pklist.append(("Golem", [80, 120, 130, 55, 65, 45], [p_types.ROCK, p_types.GROUND], [moves.BrickBreak, moves.Headbutt, moves.Bulldoze, moves.RockSlide]))
# Eeveelutions!
pklist.append(("Vaporeon", [130, 65, 60, 110, 95, 65], [p_types.WATER], [moves.Surf, moves.IceBeam, moves.Bite, moves.Headbutt]))
pklist.append(("Jolteon", [65, 65, 60, 110, 95, 130], [p_types.ELECTRIC], [moves.Thunderbolt, moves.PinMissile, moves.ShadowBall, moves.DoubleKick]))
pklist.append(("Flareon", [65, 130, 60, 95, 110, 65], [p_types.FIRE], [moves.Flamethrower, moves.IronTail, moves.QuickAttack, moves.DoubleKick]))
pklist.append(("Espeon", [65, 65, 60, 130, 95, 110], [p_types.PSYCHIC], [moves.Psychic, moves.DazzlingGleam, moves.ShadowBall, moves.Headbutt]))
pklist.append(("Umbreon", [95, 65, 110, 60, 130, 65], [p_types.DARK], [moves.Psychic, moves.IronTail, moves.QuickAttack, moves.FoulPlay]))


pklist.sort(key = sortByName)
dt = np.dtype( [('name', np.unicode_, 15), ('base_stats', int, 6), ('types', np.object_), ('moves', np.object_, 4)] )
PokemonList = np.array(pklist, dtype = dt)

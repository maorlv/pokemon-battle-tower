class PokemonType:
    def __init__(self, name):
        self.name = name
        self.super_effective = []
        self.resists = []
        self.immunities = []
    
    def defineRelations(self, super_effective = [], resists = [], immunities = []):
        self.super_effective = super_effective
        self.resists = resists
        self.immunities = immunities

    def getName(self):
        return self.name

    def getImmunities(self):
        return self.immunities

    def getSuperEffective(self):
        return self.super_effective

    def getResistance(self):
        return self.resists

    def __eq__(self, other):
        return self.name == other.name

all_types = "BUG,DARK,DRAGON,ELECTRIC,FAIRY,FIGHTING,FIRE,FLYING,GHOST,GRASS,GROUND,ICE,NORMAL,POISON,PSYCHIC,ROCK,STEEL,WATER,NOTYPE".rsplit(",")
exec("\n".join(a_type + " = PokemonType(\"" + a_type + "\")\n" for a_type in all_types))

BUG.defineRelations([DARK, PSYCHIC, GRASS], [FIGHTING, GRASS, GROUND])
DARK.defineRelations([PSYCHIC, GHOST], [DARK, GHOST], [PSYCHIC])
DRAGON.defineRelations([DRAGON], [ELECTRIC, FIRE, GRASS, WATER])
ELECTRIC.defineRelations([WATER, FLYING], [ELECTRIC, FLYING, STEEL])
FAIRY.defineRelations([DARK, DRAGON, FIGHTING], [BUG, DARK, FIGHTING])
FIGHTING.defineRelations([DARK, ICE, NORMAL, ROCK, STEEL], [BUG, DARK, ROCK])
FIRE.defineRelations([BUG, GRASS, STEEL, ICE], [FIRE, BUG, GRASS, STEEL, ICE, FAIRY])
FLYING.defineRelations([BUG, FIGHTING, GRASS], [BUG, FIGHTING, GRASS], [GROUND])
GHOST.defineRelations([GHOST, PSYCHIC], [BUG, POISON], [NORMAL, FIGHTING])
GRASS.defineRelations([WATER, ROCK, GROUND], [ELECTRIC, GRASS, GROUND, WATER])
GROUND.defineRelations([ELECTRIC, FIRE, POISON, ROCK, STEEL], [POISON, ROCK], [ELECTRIC])
ICE.defineRelations([DRAGON, FLYING, GRASS, GROUND], [ICE])
NORMAL.defineRelations([], [], [GHOST])
POISON.defineRelations([FAIRY, GRASS], [FIGHTING, POISON, BUG, GRASS])
PSYCHIC.defineRelations([FIGHTING, POISON], [PSYCHIC, FIGHTING])
ROCK.defineRelations([BUG, FIRE, FLYING, ICE], [FIRE, FLYING, NORMAL, POISON])
STEEL.defineRelations([ROCK, ICE, FAIRY], [BUG, DRAGON, FAIRY, FLYING, GRASS, ICE, NORMAL, PSYCHIC, ROCK, STEEL], [POISON])
WATER.defineRelations([FIRE, ROCK, GROUND], [FIRE, ICE, STEEL, WATER])


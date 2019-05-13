import random
import p_types
import moves
import pokemon

def sortBySpeed(elm):
    return elm['pokemon'].getSpeed()

def sortByPriority(elm):
    return elm['move'].getPriority()

class Battle:
    def __init__(self, battle_num, max_battles):
        self.difficulty = battle_num/(max_battles+1)
        self.num_of_pokemons = 0
        self.partners = []
        self.enemies = []
        self.num_of_turns = 0

    # return: sub [] of pokemonList with available mons for player
    def availableList(self):
        options = [pkmn for pkmn in pokemon.PokemonList if sum(pkmn['base_stats']) < 580]
        return options
    
    # param: @chosen - sub [] of pokemonList with chosen mons
    # return: partners[0] (to be declared as first partner) if chose 3-6 mons, None otherwise
    def selectPartners(self, chosen):
        if 3 <= len(chosen) <= 6:
            self.num_of_pokemons = len(chosen)
            for pkmn in chosen:
                name, base_stats, types, p_moves = pkmn
                partner = pokemon.Pokemon(name, base_stats, types, p_moves)
                partner.setPlayer()
                self.partners.append( partner )
            return self.partners[0]

        return None

    # return: enemies[0] to be declared as first enemy out
    def selectEnemies(self):
        # get number of enemies and number of "smart" enemies to select 
        num_of_enemies = self.num_of_pokemons
        smart_enemies_num = int(num_of_enemies * self.difficulty)

        # choose enemies according to a heuristic function to make the battle harder
        heuristics = []
        for p in range(smart_enemies_num):
            enemy, best_h = pokemon.PokemonList[0], 0
            p_min = p-1 if p > 0 else p
            p_plus = p+1 if p < len(self.partners) else p
            for m in range(len(pokemon.PokemonList)):
                cur_h = pokemon.heuristicValue(m, self.partners[p], self.partners[p_min:p_plus])
                if cur_h > best_h:
                    enemy, best_h = pokemon.PokemonList[m], cur_h
            heuristics.append(enemy)
        """print(" ".join(format(k['name']) for k in heuristics))"""

        # get the other enemies
        random_enemies = random.choices(pokemon.PokemonList, k = num_of_enemies - smart_enemies_num)
        
        # append all chosen enemies to the battle
        for pkmn in heuristics + random_enemies:
            name, base_stats, types, p_moves = pkmn
            self.enemies.append( pokemon.Pokemon(name, base_stats, types, p_moves) )

        return self.enemies[0]

    # return: [] of active partner's possible moves
    def possibleMoves(self):
        return self.partners[0].getMoves()

    # return the best move for the enemy
    def maxEnemyMove(self, hp, depth, enemyMoves, playerMoves):
        """
        Both the enemy and the player want to 1. do most damage possible to the opponent, 2. save hp as much as possible
        """
        if depth == 0:
            return hp, None
        
        current, move = {'enemy': float("inf"), 'player': float("inf")}, enemyMoves[0]
        for e_move in enemyMoves:
            m_current = {'enemy': float("inf"), 'player': float("inf")}
            for p_move in playerMoves:
                # sort by priority and speed before simulating attacks
                pokemons = [{'pokemon': self.partners[0], 'move': p_move, 'hp': hp['player'], 'mode': 'max'}, {'pokemon': self.enemies[0], 'move': e_move, 'hp': hp['enemy'], 'mode': 'min'}]
                pokemons.sort(key = sortBySpeed, reverse = True)
                pokemons.sort(key = sortByPriority, reverse = True)

                # simulate attack for player and enemy
                for i in [0,1]:
                    if pokemons[i]['hp'] > 0:
                        h_v = pokemons[i]['move'].heuristicValue(pokemons[i]['pokemon'], pokemons[1-i]['pokemon'], pokemons[i]['mode'])
                        # h_v[0] - effect on defender's hp, h_v[1] - effect on attacker's hp(recoil, etc)
                        pokemons[1-i]['hp'] = max(pokemons[1-i]['hp'] - h_v[0], 0)
                        pokemons[i]['hp'] = max(pokemons[i]['hp'] - h_v[1], 0)

                # get enemy index
                k = 0 if pokemons[0]['pokemon'] == self.enemies[0] else 1

                # simulate next attack
                d, _ = self.maxEnemyMove({'enemy': pokemons[k]['hp'], 'player': pokemons[1-k]['hp']}, depth-1, enemyMoves, playerMoves)
                
                # "choose" best scenario for player
                if (d['enemy'] < m_current['enemy']) or (d['enemy'] == m_current['enemy'] and d['player'] > m_current['player']):
                    m_current = d.copy()

            # choose best scenario for enemy -after- player's choice
            if (m_current['player'] < current['player']) or (m_current['player'] == current['player'] and m_current['enemy'] > current['enemy']):
                current, move = m_current.copy(), e_move

        return current, move

    # generate probabilty for each move according to the battle's difficulty, then pick a move for the enemy and return it
    def enemyDecideMove(self):
        enemyMoves = self.enemies[0].getMoves()
        playerMoves = self.partners[0].getMoves()

        _, best_move = self.maxEnemyMove({'enemy': self.enemies[0].getHP(), 'player': self.partners[0].getHP()}, 2, enemyMoves, playerMoves)

        best_move_prob = max(1/len(enemyMoves), self.difficulty * 1.1)
        others_prob = 1-best_move_prob
        prob_vector = []
        for move in enemyMoves:
            prob_vector.append(best_move_prob if move == best_move else others_prob/(len(enemyMoves)-1))
            #print(move.getName(), prob_vector[len(prob_vector)-1])

        move = random.choices(enemyMoves, prob_vector)[0]

        return move
        
    # param: move - selected move for partner by the player
    # return: [] of messages
    def doTurn(self, move):
        self.num_of_turns += 1
        messages = ["Turn #{}:".format(self.num_of_turns)]
        
        playerDecision = move
        
        #enemyMoves = self.enemies[0].getMoves()
        enemyDecision = self.enemyDecideMove()#random.choice(enemyMoves)

        # sort player and enemy according to the move's priority, or by speed in case of equal priority
        pokemons = [{'pokemon': self.partners[0], 'move': playerDecision}, {'pokemon': self.enemies[0], 'move': enemyDecision}]
        pokemons.sort(key = sortBySpeed, reverse = True)
        pokemons.sort(key = sortByPriority, reverse = True)

        # let every pokemon attack (unless it faints before)
        for i in [0,1]:
            if pokemons[i]['pokemon'].getHP() > 0:
                messages = messages + pokemons[i]['move'].use(pokemons[i]['pokemon'], pokemons[1-i]['pokemon'])

        return messages

    # return: [] of active hp
    def getPokemons(self):
        return [self.partners[0], self.enemies[0]]
    
    # return: False if one of lists is over (couldnt switch), True otherwise
    def switchFainted(self, faintFunc, callInFunc):
        for group in [self.enemies, self.partners]:
            if group[0].getHP() == 0:
                # switch out the fainted pokemon
                faintFunc(not group[0].isEnemy())

                # switch in next pokemon in group
                group.pop(0)
                if len(group) > 0:
                    callInFunc(group[0], len(group))

        # check if one of the groups is over            
        return len(self.enemies) > 0 and len(self.partners) > 0

    # return: True if the player won, False otherwise
    # notice: for us, tie == victory :)
    def playerWin(self):
        if len(self.enemies) == 0:
            return True
        return False





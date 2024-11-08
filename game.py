from consts import *
from gui import GameGUI

import copy
import random
import traceback
from collections import defaultdict
from timeit import default_timer as timer

class Map:
    def __init__(self, size, players, obj_proportion):
        self.size = size
        self.gameObject = []
        self.bots = [Bot(player, i) for i, player in enumerate(players)]
        self.num_players = len(players)

        self.max_gameObject = int(obj_proportion * self.size ** 2)
        self.gameObject_assignments = None

        self.gen_map()

    def gen_map(self):
        cts = [1, 3, 5, 7, 9, 11, 13]
        cts = [ct for ct in cts]
        cts = random.choices(cts, k=3)
        random.shuffle(cts)
        self.num_gameObjects = {
            obj_type: cts[i] for i, obj_type in enumerate(GAMEOBJECT_TYPES)
        }
        overage = sum(self.num_gameObjects.values()) - self.max_gameObject
        if overage > 0:
            for obj, val in self.num_gameObjects.items():
                self.num_gameObjects[obj] -= (overage//3)-1
                if self.num_gameObjects[obj] <= 0:
                    self.num_gameObjects[obj] = 1
        #print(self.num_gameObjects, sum(self.num_gameObjects.values()), self.max_gameObject)
        gameObject_pos = []
        
        for obj_type in self.num_gameObjects:
            for i in range(self.num_gameObjects[obj_type]):
                while True:
                    candidate = (random.randint(0, self.size-1), random.randint(0, self.size-1))
                    if candidate not in gameObject_pos:
                        gameObject_pos.append(candidate)
                        gameObject = GameObject((candidate[0], candidate[1]), GAMEOBJECT_TYPES[obj_type])
                        self.gameObject.append(gameObject)
                        break

        for i in range(self.num_players):
            while True:
                candidate = (random.randint(0, self.size-1), random.randint(0, self.size-1))
                if candidate not in gameObject_pos:
                    self.bots[i].set_pos(candidate)
                    break

class Engine:
    def __init__(self, players, map_size, max_turns, obj_proportion):
        self.turn = 0
        self.MAX_TURNS = max_turns
        self.map = Map(map_size, players, obj_proportion)

    def get_state(self, player_idx=-1):
        map_vec = [[[] for j in range(self.map.size)] for i in range(self.map.size)]
        
        tops = self.get_category_tops()
        for i, bot in enumerate(self.map.bots):
            bot.category_tops = tops[i]
            bot = Bot(None, bot.i, bot.position, bot.collected_objects, bot.prev_collected_objects, bot.category_tops)
            bot.name = self.map.bots[i].player.name
            bot.group = self.map.bots[i].player.group
            map_vec[bot.position[0]][bot.position[1]].append(bot)
        
        for gameObject in self.map.gameObject:
            obj = GameObject(gameObject.position, gameObject.obj_type)
            map_vec[gameObject.position[0]][gameObject.position[1]] = [obj]
                
        return GameState(self.map.bots, map_vec, self.turn)
    
    def step(self, action):
        if self.turn > self.MAX_TURNS:
            return GameStatus.TIMEOUT
        self.turn += 1

        gameObject_collected = False
        players = list(action)
        random.shuffle(players)
        for player_idx in players:
            #assert type(player_idx) is int
            #assert type(action[player_idx]) is int

            bot_pos = self.map.bots[player_idx].position
            pos_delta = [0, 0]
            act = action[player_idx]
            if act == ACTIONS["up"]:
                pos_delta[0] -= 1
            elif act == ACTIONS["down"]:
                pos_delta[0] += 1
            elif act == ACTIONS["left"]:
                pos_delta[1] -= 1
            elif act == ACTIONS["right"]:
                pos_delta[1] += 1

            new_pos = (bot_pos[0] + pos_delta[0], bot_pos[1] + pos_delta[1])
            
            valid_move = 0 <= new_pos[0] < self.map.size and 0 <= new_pos[1] < self.map.size
            if not valid_move:
                continue
            
            self.map.bots[player_idx].position = new_pos
            for gameObject in self.map.gameObject:
                if gameObject.position == new_pos:
                    self.map.bots[player_idx].add_object(gameObject.obj_type)
                    self.map.gameObject.remove(gameObject)
                    gameObject_collected = True

            if len(self.map.gameObject) == 0:
                return GameStatus.ALL_GAMEOBJECTS_COLLECTED
        
        if gameObject_collected:
            return GameStatus.GAMEOBJECT_COLLECTED
        return GameStatus.IN_PROGRESS
    
    def get_category_tops(self):        
        top_per_category = defaultdict(int)
        top_players = defaultdict(list)
        
        for bot in self.map.bots:
            for i, cat in enumerate(GAMEOBJECT_TYPES):
                if bot.collected_objects[i] > top_per_category[cat]:
                    top_players[cat] = []
                if bot.collected_objects[i] >= top_per_category[cat]:
                    top_players[cat].append(bot)
                    top_per_category[cat] = bot.collected_objects[i]
        num_tops = [0] * len(self.map.bots)
        for cat in top_players:
            tops = top_players[cat]
            if len(tops) > 1: # skip ties
                continue
            top_bot = tops[0]
            num_tops[top_bot.i] += 1
        return num_tops
    
    def start(self, show_gui, check_timing):
        if show_gui:
            gui = GameGUI(2, (self.map.size, self.map.size))
            gui.start(self.map.num_players)
        
        status = GameStatus.IN_PROGRESS
        timings = defaultdict(int)
        while status in [GameStatus.IN_PROGRESS, GameStatus.GAMEOBJECT_COLLECTED]:
            state = self.get_state()
            if show_gui:
                gui.update_screen(state)
            actions = {}
            for i in range(len(self.map.bots)):
                if check_timing:
                    start = timer()
                
                # call bot's step method
                try:
                    x = self.map.bots[i].step(state.map, state.turn)
                except:
                    raise ValueError(f"The step method for the player <{self.map.bots[i].player.name}> raised an exception. The traceback is as follows:\n{traceback.format_exc()}")
                
                if check_timing:
                    end = timer()
                    diff = end - start
                    timings[self.map.bots[i].name] += diff
                
                if x not in ACTIONS:
                    raise ValueError(f"The step method for the player <{self.map.bots[i].player.name}> did not return a valid directional string; instead, <{x}> was returned.")
                actions[i] = ACTIONS[x]
            
            status = self.step(actions)
            if show_gui and status == GameStatus.GAMEOBJECT_COLLECTED:
                gui.play_sound('collect')
        
        state = self.get_state()
        if show_gui:
            if status == GameStatus.ALL_GAMEOBJECTS_COLLECTED:
                gui.play_sound('gameover')
            gui.update_screen(state, game_over=True)
            gui.stop()
        
        #if status == GameStatus.TIMEOUT:
        #    print("*** max turns reached")
        
        max_tops = max([bot.category_tops for bot in state.bots])
        winners = [bot.name for bot in self.map.bots if bot.category_tops == max_tops]
        if len(winners) > 1:
            winners = []
        return winners, timings, state.turn

def main(players, map_size, max_turns, obj_proportion, show_gui, check_timing):
    engine = Engine(players, map_size, max_turns, obj_proportion)    
    return engine.start(show_gui=show_gui, check_timing=check_timing)

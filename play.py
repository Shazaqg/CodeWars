# v1.4
# December 1

# Changelog
# 1.0: initial release
# 1.1: fix for windows
# 1.2: fix GUI showing transposed grid; fix for two bots in same location (now each position is a list); add pretty_print function.
# 1.2.2: fix movement issue, better exception message for invalid return value
# 1.3: new bot attributes: previously_collected_bots, category_tops(int), name, group; tie in individual categories is considered loss.
# 1.4: prevent cheating; fix "grop" (group) attribute typo for bot objects; add get_dx_dy_between_points func to consts.py; shuffle players list after every game; fix GUI for large map sizes; add MAX_TURNS and MAX_OBJ_PROPORTION variables below; modified random range of number of starting objects; speed optimizations.

import random
from game import main
from importlib import util
from collections import defaultdict

##
# You can modify the variables below to change various properties of the game.
##

NUM_GAMES = 100
MAP_SIZE = 15
GUI = False
CHECK_TIMING = False
PLAYER_MODULES = ['random_player', 'random_player', 'ai_player']
MAX_TURNS = 200
MAX_OBJ_PROPORTION = 0.15
VERSION = "1.4"

##
# Do not change any lines below.
##

def run(num_games, map_size, gui, check_timing, player_modules, max_turns, obj_proportion):
    player_modules = list(enumerate(player_modules))
    wins = defaultdict(int)
    times = defaultdict(int)
    for i in range(num_games):
        players = []
        random.shuffle(player_modules)
        for j, (k, player_module) in enumerate(player_modules):
            spec = util.spec_from_file_location("module.name", player_module + ".py")
            foo = util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            players.append(foo.Player())
            players[-1].name = f"Player {k}: {players[-1].name} ({j})"
    
        winners, timings, final_turn = main(players, map_size, max_turns, obj_proportion, show_gui=gui, check_timing=check_timing)
        print(f"Game {i+1}: {winners}")
        for w in winners:
            wins[w.split(" (")[0]] += 1
        for t in timings:
            times[t.split(" (")[0]] += timings[t] / final_turn
    
    game_feedback = f"The results of the {num_games} games were as follows:\n"
    game_feedback += '\n'.join([f"{w}: {wins[w]}" for w in wins])
    print(game_feedback)
    
    timing_feedback = ''
    if check_timing:
        timing_feedback = f"It took the following average number of seconds for each player's step method to be executed:\n"
        timing_feedback += '\n'.join([f"{t}: {times[t]}" for t in times])
        print(timing_feedback)
    
    return game_feedback, timing_feedback, wins, times

if __name__ == '__main__':
    run(NUM_GAMES, MAP_SIZE, GUI, CHECK_TIMING, PLAYER_MODULES, MAX_TURNS, MAX_OBJ_PROPORTION)
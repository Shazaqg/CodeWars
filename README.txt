ai_player.py and random_player.py: These define bot behaviors for the game. The RandomPlayer chooses actions randomly, while ai_player.py presumably contains more sophisticated strategies.
consts.py: This file likely contains constants used throughout the game, such as movement directions or game object types.
game.py: This is the game engine. It handles the map generation, bot placement, game object collection, and turn-based logic. It defines the Map class for creating the game environment and the Engine class to run the game.
gui.py: Implements a graphical user interface using pygame. It displays the game board, updates the screen, draws grid objects, and shows scores.
play.py: Acts as the main entry point for running the simulation. It sets up the game parameters, loads player modules, and executes multiple games. It tracks wins and times, printing a summary of results.

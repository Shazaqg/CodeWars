
from consts import *


GAMEOBJECT_TYPES = {
    "banana": 0,
    "coin": 1,
    "cauldron": 2
}

class Player(GamePlayer):
    def __init__(self):
        self.name = "Pikachu"
        self.group = "26A"
        self.obj_values = [0, 0, 0]
        self.total_game_objs = None
        self.map_size = 0
        
    def get_my_bot(self, game_map, cur_pos):
        ''' (list, typle) -> Bot
        Returns the Bot object for this player.
        '''
        i, j = cur_pos
        bots = game_map[i][j]
        assert len(bots) != 0
        for bot in bots:
            if bot.i == self.i:
                return bot

    def get_all_bots(self, game_map): #Betty
        ''' (list) -> list<BotObject>
        Returns a list of the BotObjects on the map.
        '''
        bots = []
        for i in range(len(game_map)):
            for j in range(len(game_map[i])):
                for item in game_map[i][j]:
                    if type(item) is Bot:
                        bots.append(item)
        return bots
    
    def get_all_game_objects(self, game_map): #Betty
        ''' (list) -> list<BotObject>
        Returns a list of the GameObjects on the map.
        '''
        game_objs = []
        for i in range(len(game_map)):
            for j in range(len(game_map[i])):
                for item in game_map[i][j]:
                    if type(item) is GameObject:
                        game_objs.append(item)
        return game_objs
    
    def get_distances_to_objects(self, game_map, cur_pos): # Betty
        ''' (list) -> dict<GameObject: int>
        Returns a dictionary where the keys are GameObjects
        and the value for a GameObject is its distance to the
        current player.
        '''
        game_objects = self.get_all_game_objects(game_map)
        distances = dict()
        for obj in game_objects:
            obj_pos = obj.position
            distances[obj] = abs(cur_pos[0] - obj_pos[0]) + abs(cur_pos[1] - obj_pos[1])
        return distances
    
    def get_nearest_bot(self, game_map, position):
        ''' (list, tuple<int, int>) -> Bot
        Returns the nearest Bot object to the given position.
        '''
        all_bots = self.get_all_bots(game_map)
        smallest_distance = 0
         
        for bot in all_bots:
            if smallest_distance == 0:
                smallest_distance = abs(position[0] - bot.position[0])+ abs(position[1] - bot.position[1])
                nearest_bot = bot
            else:
                distance = abs(position[0] - bot.position[0])+ abs(position[1] - bot.position[1])
                if distance < smallest_distance:
                    smallest_distance = distance
                    nearest_bot = bot
                
        return nearest_bot

    
    def get_total_available_objects(self, game_map, obj_type):
        ''' (list<int>) -> int
        Returns the total available number of the given object type.
        Returns the total of all obj types if obj_type == -1
        '''
        game_objs = self.get_all_game_objects(game_map)

        if obj_type == -1:
            return len(game_objs)
        
        count = 0
        for obj in game_objs:
            if obj.obj_type == obj_type:
                count += 1
        return count
        
    def get_total_objects(self, obj_type): 
        ''' (list<int>, int) -> int
        Returns the total number of the given GameObject type, including objects
        both on the grid and those that have already been picked up.
        If obj_type = -1, returns the total number of game objs.
        '''
        if obj_type == -1:
            x, y, z = self.total_game_objs
            return x+y+z
        return self.total_game_objs[obj_type]

    def get_obj_values(self): 
        ''' (list) -> NoneType
        Assigns a float in [0, 1] corresponding to the value of gaining one GameObject of that type.
        
        E.g. If there is 1 banana, 4 coins, and 5 cauldrons, the attribute self.obj_values will be
        set to [1.0, 0.25, 0.2] because 1/1 = 1, 1/4 = 0.25, and 1/5 = 0.2.
        So the banana is the most valuable in this case because it has a value of 1.
        '''
        for i in range(len(self.obj_values)):
            self.obj_values[i] = 1/self.total_game_objs[i]
    
    def update_obj_values(self, game_map, cur_pos):
        '''
        This function does not return anything. It only updates the self.obj_values attribute
        to reflect the new object values.
            
        More specifically:
            -if more than 50% of an object has been collected, its value changes to 0.0.
            -if our bot only needs one more of an object to get 50% or more of that object, its value changes to 1.0
            -if some other bot only needs one more of an object to get 50% or more of that object, its value changes to __?
        '''
        my_bot = self.get_my_bot(game_map, cur_pos)
        for i in range(len(self.obj_values)):
            avail_objs = self.get_total_available_objects(game_map, i)
            if (avail_objs/self.total_game_objs[i]) < 0.5:  
                self.obj_values[i] = 0
                
            #If someone only needs one more object in that category to be winning in that category,
            #its value changes to 1.0:
            #elif (my_bot.collected_objects[i]+1)/self.total_game_objs[i] > 0.5:
            elif (avail_objs+1)/self.total_game_objs[i] >= 0.5:
                self.obj_values[i] = 10
                
    def get_best_game_obj(self, game_map, cur_pos):
        '''combines the distance points and obj_values to return the game_obj with the greatest total value'''
        distances = self.get_distances_to_objects(game_map, cur_pos)
        
        scale = 100 # change this depending on the map size
        best_value = -1
        for obj in distances:
            if self.obj_values[obj.obj_type] == 0:
                value = 0
            else:
                value = self.map_size / ((scale * distances[obj])*self.obj_values[obj.obj_type])
                
            if value > best_value:
                best_obj = obj
        
        return best_obj
    
    def get_closest_game_obj(self, game_map, cur_pos):
        ''' (list, tuple<int, int>) -> Bot
        Returns the closest_game_obj with highest value.
        '''
        distances = self.get_distances_to_objects(game_map, cur_pos)
        obj_list = list(distances.items()) # should be a list of tuples of length 2, where the fisrt is the gameobj and the second is its distance
        #print('obj_list', obj_list)
        
        best_obj, closest_distance = obj_list[0][0], obj_list[0][1]
        closest_objs = [best_obj]
        for obj, distance in obj_list:
            if (self.obj_values[obj.obj_type] != 0) and distance < closest_distance:
                closest_objs = [obj]
            elif distance == closest_distance:
                closest_objs.append(obj)
        
        best_value = -1
        for obj in closest_objs:
            value = self.obj_values[obj.obj_type]
            if value > best_value:
                best_value = value
                best_obj = obj
        return best_obj
      
    def step(self, game_map, turn, cur_pos):
        #print("turn: ", turn)
        #print("cur_pos: ", cur_pos)
        #pretty_print(game_map)
        
        my_bot = self.get_my_bot(game_map, cur_pos)
        my_collected_objs = my_bot.collected_objects
        nearest_bot = self.get_nearest_bot(game_map, cur_pos)  

        if turn == 0: # this sets the total_game_objs attribute for the current game
            bananas = self.get_total_available_objects(game_map, 0)
            coins = self.get_total_available_objects(game_map, 1)
            cauldrons = self.get_total_available_objects(game_map, 2)
            self.total_game_objs = (bananas, coins, cauldrons) # e.g. if there are 5 bananas, 3 coins, 2 cauldrons, this should be (5, 3, 2)
            self.map_size = len(game_map)*len(game_map[0])
            self.get_obj_values()
            
        self.update_obj_values(game_map, cur_pos)            
        
        #best_obj = self.get_best_game_obj(game_map, cur_pos)
        best_obj = self.get_closest_game_obj(game_map, cur_pos) 
        move_to = best_obj.position
        #print("move_to", move_to)
        dy, dx = get_dx_dy_between_points(move_to, cur_pos)
        #print('dy, dx', dy, dx)
        #return "up"
        action = get_action_for_delta(dx, dy) # dx and dy are reversed in this function
        return action

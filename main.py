# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import math
import sys
import random
import typing
import numpy as np
from collections import deque
import copy


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#E80978",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

def distance_of_food(my_head,food):
    return ( (my_head["x"]-food["x"])**2 + (my_head["y"]-food["y"])**2 )**0.5

class Point:
    def __init__(self):
        self.x = 0
        self.y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'
        
class Snake:
    def __init__(self):
        self.health = 0
        self.pos = deque([])

class Game:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.snakes = [] # 0th snake is always us, rest are the opponent/s
        self.snakes.append(Snake()) # us
        self.foodList = []

    def isValid(self, s, move):
        valid = True
        head = self.snakes[s].pos[0]
        nextHead = Point(head.x+move[0], head.y+move[1])

        # Check for boundary collisions
        if nextHead.x < 0 or nextHead.x >= self.width or nextHead.y < 0 or nextHead.y >= self.height:
            valid = False
        
        if valid:
            for snake in self.snakes:
                for p in snake.pos:
                    if nextHead.x == p.x and nextHead.y == p.y:
                        valid = False
                        break

        # Check for self collisions
        '''if valid:
            for p in self.snakes[s].pos:
                if nextHead.x == p.x and nextHead.y == p.y:
                    valid = False
                    break

        # Check for collision with the opponent
        if valid:
            if len(self.snakes) > 1:
                opponent = 1
                if s == 0:
                    opponent = 1
                else:
                    opponent = 0
                for p in self.snakes[opponent].pos:
                    if nextHead.x == p.x and nextHead.y == p.y:
                        valid = False
                        break'''

        return valid

    def moveOptions(self, s: int):
        moveList = []
        if self.isValid(s, (-1,0)):
            moveList.append((-1,0))
        if self.isValid(s, (1,0)):
            moveList.append((1,0))
        if self.isValid(s, (0,-1)):
            moveList.append((0,-1))
        if self.isValid(s, (0,1)):
            moveList.append((0,1))
        return moveList
        
    def moveSnake(self, s, move):
        # Deep copy current game state
        copyGame = copy.deepcopy(self)

        # Get head position for player s
        head = copyGame.snakes[s].pos[0]

        # Generate next head position for player s
        nextHead = Point(head.x+move[0], head.y+move[1])
        
        # Add the next head position to the player s position deque
        copyGame.snakes[s].pos.appendleft(nextHead)

        # Decrease player s health by 1
        copyGame.snakes[s].health -= 1

        # Check if any food is consumed.
        # Any non-consumed food is added to foodList
        foodList = []
        ateFood = False
        for food in copyGame.foodList:
            if food.x == nextHead.x and food.y == nextHead.y:
                ateFood = True
            else:
                foodList.append(food)
 
        if ateFood:
            # If player s ate food, make the health 100 and don't remove the tail element
            copyGame.snakes[s].health = 100
        else:
            # If plater s did not eat food, remove the tail element
            copyGame.snakes[s].pos.pop()
            
        # Set the unconsumed food in the copyGame
        copyGame.foodList = foodList

        return copyGame
    
    def isDead(self, player, moveList):
        return len(moveList) == 0 or self.snakes[player].health == 0

    def checkDeadSnake(self, moveLists):
        deadList = []
        for i in range(len(self.snakes)):
            deadList.append(False)

        for i in range(len(self.snakes)):
            for j in range(len(self.snakes)):
                if i != j:
                    isHeadCollision = self.snakes[i].pos[0].x == self.snakes[j].pos[0].x and self.snakes[i].pos[0].y == self.snakes[j].pos[0].y
        
                    if isHeadCollision:
                        if len(self.snakes[i].pos) > len(self.snakes[j].pos):
                            deadList[j] = True
                        else:
                            deadList[i] = True
        
        for i in range(len(self.snakes)):
            deadList[i] = deadList[i] or len(moveLists[i]) == 0 or self.snakes[i].health == 0

        return deadList
    
    def heuristic(self, player, deadList):
        score = 0.0
        if deadList[0]:
            score = -math.inf
        elif True in deadList[1:]:
            score = math.inf
        else:
            #return float(self.snakes[player].health)
            # Only when health or length is less than certain threshold, give priority to food. Otherwise avoid food.
            needToLengthen = False
            for s in self.snakes:
                if s != self.snakes[player]:
                    if len(self.snakes[player].pos) < len(s.pos):
                        needToLengthen = True

            health = self.snakes[player].health
            length = float(len(self.snakes[player].pos))
            if health < 50 or needToLengthen:
                head = self.snakes[player].pos[0]
                minInvDist = -math.inf
                for food in self.foodList:
                    dist = abs(food.x-head.x) + abs(food.y-head.y)
                    invDist = 1.0 if dist == 0 else 1.0/float(dist)
                    if minInvDist < invDist:
                        minInvDist = invDist
                    score = minInvDist + float(self.snakes[player].health)/100.0
            else:
                score = float(len(self.moveOptions(player)))
            
        return score
        
    def minmaxMove(self, depth):
        if len(self.snakes) == 1:
            moveList0 = self.moveOptions(0)
            bestScore = -math.inf
            bestMove = None
            for move in moveList0:
                newGame = self.moveSnake(0, move)
                newGameMoveList0 = newGame.moveOptions(0)
                newGameDeadList = newGame.checkDeadSnake([newGameMoveList0])
                score = newGame.heuristic(0, newGameDeadList)
                if bestScore < score:
                    bestScore = score
                    bestMove = move
            return (bestScore, bestMove)
        else:
            moveList0 = self.moveOptions(0)
            moveList1 = self.moveOptions(1)
            deadList = self.checkDeadSnake([moveList0, moveList1])
            return self.minmaxMoveRecursive(depth, 0, moveList0, moveList1, deadList)

    def nextPlayer(self, player):
        n = len(self.snakes)
        return (player+1)%n

    def minmaxMoveRecursive(self, depth, player, moveList0, moveList1, deadList):
        if depth == 0 or deadList[0] or deadList[1]:
            return (self.heuristic(player, deadList), None)
        if player == 0:
            bestScore = -math.inf
            bestMove = None
            for move in moveList0:
                newGame = self.moveSnake(player, move)
                newGameMoveList0 = newGame.moveOptions(0)
                newGameMoveList1 = newGame.moveOptions(1)
                newGameDeadList = newGame.checkDeadSnake([newGameMoveList0, newGameMoveList1])
                (newGameScore, newGameMove) = newGame.minmaxMoveRecursive(depth-1, newGame.nextPlayer(player), newGameMoveList0, newGameMoveList1, newGameDeadList)
                if bestScore < newGameScore:
                    bestScore = newGameScore
                    bestMove = move
            return (bestScore, bestMove)
        else:
            bestScore = math.inf
            bestMove = None
            for move in moveList1:
                newGame = self.moveSnake(player, move)
                newGameMoveList0 = newGame.moveOptions(0)
                newGameMoveList1 = newGame.moveOptions(1)
                newGameDeadList = newGame.checkDeadSnake([newGameMoveList0, newGameMoveList1])
                (newGameScore, newGameMove) = newGame.minmaxMoveRecursive(depth-1, newGame.nextPlayer(player), newGameMoveList0, newGameMoveList1, newGameDeadList)
                if bestScore > newGameScore:
                    bestScore = newGameScore
                    bestMove = move
            return (bestScore, bestMove)
            
            
        
# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    g = Game()
    g.width = game_state['board']['width']
    g.height = game_state['board']['height']
    g.snakes[0].health = game_state["you"]["health"]
    for s in game_state["you"]["body"]:
        g.snakes[0].pos.append(Point(s["x"], s["y"]))

    snakes = game_state['board']['snakes']
    for snake in snakes:
        if snake["id"] != game_state["you"]["id"]:
            g.snakes.append(Snake())
            g.snakes[1].health = snake["health"]
            for s in snake["body"]:
                g.snakes[1].pos.append(Point(s["x"], s["y"]))
    
    for food in game_state["board"]["food"]:
        g.foodList.append(Point(food["x"], food["y"]))

    # Depth of 4 seems optimal for the current heuristic
    (score, move) = g.minmaxMove(4)
    if move == None:
        moveList = g.moveOptions(0)
        move = random.choice(moveList)

    print(move)
    
    if move == (-1,0):
        return {"move":"left"}
    elif move == (1,0):
        return {"move":"right"}
    elif move == (0,-1):
        return {"move":"down"}
    elif move == (0,1):
        return {"move":"up"}
    else:
        return {"move":"up"}

    '''moveList = g.moveOptions(0)

    if len(moveList) > 0:
        move = random.choice(moveList)
        if move == (-1,0):
            return {"move":"left"}
        elif move == (1,0):
            return {"move":"right"}
        if move == (0,-1):
            return {"move":"down"}
        elif move == (0,1):
            return {"move":"up"}
        else:
            return {"move":"up"}
    else:
        return {"move":"up"}'''

    #moves = move_options(game_state)
    #if moves[0] == 1:
    #    return {"move", "left"}
    #elif moves[1] == 1:
    #    return {"move", "right"}
    #elif moves[2] == 1:
    #    return {"move", "down"}
    #elif moves[3] == 1:
    #    return {"move", "up"}

    '''is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    if my_head["x"] == board_width-1:
        is_move_safe["right"] = False
    if my_head["x"] == 0:
        is_move_safe["left"] = False
    if my_head["y"] == board_height-1:
        is_move_safe["up"] = False
    if my_head["y"] == 0:
        is_move_safe["down"] = False

    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body']
    for segment in my_body[1:]:
        if segment["x"] == my_head["x"] + 1 and segment["y"] == my_head["y"]:
            is_move_safe["right"] = False
        elif segment["x"] == my_head["x"] + 2 and segment["y"] == my_head["y"]:
            is_move_safe["right"] = False
        elif segment["x"] == my_head["x"] + 3 and segment["y"] == my_head["y"]:
            is_move_safe["right"] = False
        if segment["x"] == my_head["x"] - 1 and segment["y"] == my_head["y"]:
            is_move_safe["left"] = False
        elif segment["x"] == my_head["x"] - 2 and segment["y"] == my_head["y"]:
            is_move_safe["left"] = False
        elif segment["x"] == my_head["x"] - 3 and segment["y"] == my_head["y"]:
            is_move_safe["left"] = False
        if segment["y"] == my_head["y"] + 1 and segment["x"] == my_head["x"]:
            is_move_safe["up"] = False
        elif segment["y"] == my_head["y"] + 2 and segment["x"] == my_head["x"]:
            is_move_safe["up"] = False
        elif segment["y"] == my_head["y"] + 3 and segment["x"] == my_head["x"]:
            is_move_safe["up"] = False
        if segment["y"] == my_head["y"] - 1 and segment["x"] == my_head["x"]:
            is_move_safe["down"] = False
        elif segment["y"] == my_head["y"] - 2 and segment["x"] == my_head["x"]:
            is_move_safe["down"] = False
        elif segment["y"] == my_head["y"] - 3 and segment["x"] == my_head["x"]:
            is_move_safe["down"] = False

    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']

    for opponent in opponents:
        e
        for segment in opponent["body"]:
            # Check for whether right move is safe_move is saf
            if segment["x"] == my_head["x"] + 1 and segment["y"] == my_head["y"]:
                is_move_safe["right"] = False
            # Check for whether left move is safe
       
            if segment["x"] == my_head["x"] - 1 and segment["y"] == my_head["y"]:
                is_move_safe["left"] = False
            # Check for whether up move is safe
       
            if segment["y"] == my_head["y"] + 1 and segment["x"] == my_head["x"]:
                is_move_safe["up"] = False
            # Check for whether down move is safe
       
            if segment["y"] == my_head["y"] - 1 and segment["x"] == my_head["x"]:
                is_move_safe["down"] = False

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']
                      }: No safe moves detected! Moving down")
        print("head is at ", my_head["x"], " ", my_head["y"])
        return {"move": "down"}

    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    food = game_state['board']['food']
    closest_food = food[0]
    minimum_distance = distance_of_food(my_head,food[0])
    if(len(food > 1)):
        for i in range(1,len(food)):
            dist = distance_of_food(my_head,food[i])
            if(dist < minimum_distance]):
                closest_food = food[i]
                minimum_distance = dist




    print(f"MOVE {game_state['turn']}: {next_move}")
    print(safe_moves)
    return {"move": next_move}'''


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})

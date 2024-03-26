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
        "author": "SlytherinSeeker",  # TODO: Your Battlesnake Username
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
    # Euclidean distance from food
    return ( (my_head["x"]-food["x"])**2 + (my_head["y"]-food["y"])**2 )**0.5

class Point:
    # Object Point has attribute x and y 
    def __init__(self):
        self.x = 0
        self.y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'
        
class Snake:
    # Object Snake has attribute health and pos
    def __init__(self):
        self.health = 0
        self.pos = deque([]) # deque object is easier to handle for to append and pop with O(1)

class Game:
    # Object Game has the attributes of the gameboard which are required just for simulation in minmax algorithm
    def __init__(self):
        self.width = 0
        self.height = 0
        self.snakes = [] # 0th snake is always us, rest are the opponent/s
        self.snakes.append(Snake()) # us
        self.foodList = []

    def isValid(self, s, move):
        # isValid() Checks whether the move is valid. Returns true or false
        valid = True
        head = self.snakes[s].pos[0]
        nextHead = Point(head.x+move[0], head.y+move[1])

        # Check for boundary collisions
        if nextHead.x < 0 or nextHead.x >= self.width or nextHead.y < 0 or nextHead.y >= self.height:
            valid = False
        
        # Check for body collisions with itslef and other snakes
        if valid:
            for snake in self.snakes:
                for p in snake.pos:
                    if nextHead.x == p.x and nextHead.y == p.y:
                        valid = False
                        break

        return valid

    def moveOptions(self, s: int):
        # moveOptions chechks which move is valid and returns a list of valid moves.
        moveList = []
        if self.isValid(s, (-1,0)):
            # left move is valid
            moveList.append((-1,0))
        if self.isValid(s, (1,0)):
            # right move is valid
            moveList.append((1,0))
        if self.isValid(s, (0,-1)):
            # down move is valid
            moveList.append((0,-1))
        if self.isValid(s, (0,1)):
            # up move is valid
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
    

    def checkDeadSnake(self, moveLists):
        # Checks if any move makes the snake dead. Returns a list of booleans as a status of snake's living or death.
        # Snake is dead when it collides with other snake or boundary or when it has no valid move left.
        deadList = []
        for i in range(len(self.snakes)):
            deadList.append(False)

        # Check whether the snake is colliding
        for i in range(len(self.snakes)):
            for j in range(len(self.snakes)):
                if i != j:
                    isHeadCollision = self.snakes[i].pos[0].x == self.snakes[j].pos[0].x and self.snakes[i].pos[0].y == self.snakes[j].pos[0].y
        
                    if isHeadCollision:
                        if len(self.snakes[i].pos) > len(self.snakes[j].pos):
                            deadList[j] = True
                        else:
                            deadList[i] = True
        
        # Check whether any valid moves are left
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
            # Only when health or length is less than certain threshold, give more weightage to food.
            # This strategy is implemented to make sure that the snake does not get too long.
            needToLengthen = False

            # Check if the snakes length is less that the opponent snake's length
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
                # Give weightage to the move which has more valid moves available.
                score = float(len(self.moveOptions(player)))
            
        return score
        
    def minmaxMove(self, depth):
        # When there is only one snake on the board
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
        # For when there are 2 snakes on the board
        else:
            moveList0 = self.moveOptions(0)
            moveList1 = self.moveOptions(1)
            deadList = self.checkDeadSnake([moveList0, moveList1])
            return self.minmaxMoveRecursive(depth, 0, moveList0, moveList1, deadList)

    def nextPlayer(self, player):
        # Change the player for the turn
        n = len(self.snakes)
        return (player+1)%n

    def minmaxMoveRecursive(self, depth, player, moveList0, moveList1, deadList):
        # Check if condition is terminal
        if depth == 0 or deadList[0] or deadList[1]:
            return (self.heuristic(player, deadList), None)
        # Maximizing player turn
        if player == 0:
            bestScore = -math.inf
            bestMove = None
            for move in moveList0:
                # moveSnake() returns the simulated game board
                newGame = self.moveSnake(player, move)
                newGameMoveList0 = newGame.moveOptions(0)
                newGameMoveList1 = newGame.moveOptions(1)
                newGameDeadList = newGame.checkDeadSnake([newGameMoveList0, newGameMoveList1])
                (newGameScore, newGameMove) = newGame.minmaxMoveRecursive(depth-1, newGame.nextPlayer(player), newGameMoveList0, newGameMoveList1, newGameDeadList)
                # Find out which move has the highest score
                if bestScore < newGameScore:
                    bestScore = newGameScore
                    bestMove = move
            # Return the best move and score for that turn
            return (bestScore, bestMove)
        else:
            bestScore = math.inf
            bestMove = None
            # Minimizing player turn
            for move in moveList1:
                newGame = self.moveSnake(player, move)
                newGameMoveList0 = newGame.moveOptions(0)
                newGameMoveList1 = newGame.moveOptions(1)
                newGameDeadList = newGame.checkDeadSnake([newGameMoveList0, newGameMoveList1])
                (newGameScore, newGameMove) = newGame.minmaxMoveRecursive(depth-1, newGame.nextPlayer(player), newGameMoveList0, newGameMoveList1, newGameDeadList)
                # Find out which move has lowest score
                if bestScore > newGameScore:
                    bestScore = newGameScore
                    bestMove = move
            # Return the best move and score for the turn
            return (bestScore, bestMove)
            
            
        
# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    # Create Game Object
    g = Game()
    g.width = game_state['board']['width']
    g.height = game_state['board']['height']
    g.snakes[0].health = game_state["you"]["health"]

    # Locate the Snake Object
    for s in game_state["you"]["body"]:
        g.snakes[0].pos.append(Point(s["x"], s["y"]))

    snakes = game_state['board']['snakes']
    for snake in snakes:
        # Make sure that the id of our snake in the game is at 0th position and rest other snakes are after that.
        if snake["id"] != game_state["you"]["id"]:
            g.snakes.append(Snake())
            g.snakes[1].health = snake["health"]
            for s in snake["body"]:
                g.snakes[1].pos.append(Point(s["x"], s["y"]))

    # Create the foodlist
    for food in game_state["board"]["food"]:
        g.foodList.append(Point(food["x"], food["y"]))

    # Depth of 4 seems optimal for the current heuristic
    (score, move) = g.minmaxMove(4)
    
    # If minmax fails , choose a move randomly
    if move == None:
        moveList = g.moveOptions(0)
        move = random.choice(moveList)

    
    # Return the chosen move to the game
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

    

  
# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})

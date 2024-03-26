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
        "author": "Slytherin Seeker",  # TODO: Your Battlesnake Username
        "color": "#E9B63E",  # TODO: Choose color
        "head": "fang",  # TODO: Choose head
        "tail": "hook",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


def distance_of_food(my_head, food):
    return ((my_head["x"]-food["x"])**2 + (my_head["y"]-food["y"])**2)**0.5


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
        self.snakes = []  # 0th snake is always us, rest are the opponent/s
        self.snakes.append(Snake())  # us
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
        

        return valid

    def moveOptions(self, s: int):
        moveList = []
        if self.isValid(s, (-1, 0)):
            moveList.append((-1, 0))
        if self.isValid(s, (1, 0)):
            moveList.append((1, 0))
        if self.isValid(s, (0, -1)):
            moveList.append((0, -1))
        if self.isValid(s, (0, 1)):
            moveList.append((0, 1))
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
                    isHeadCollision = self.snakes[i].pos[0].x == self.snakes[j].pos[
                        0].x and self.snakes[i].pos[0].y == self.snakes[j].pos[0].y

                    if isHeadCollision:
                        if len(self.snakes[i].pos) > len(self.snakes[j].pos):
                            deadList[j] = True
                        else:
                            deadList[i] = True

        for i in range(len(self.snakes)):
            deadList[i] = deadList[i] or len(
                moveLists[i]) == 0 or self.snakes[i].health == 0

        return deadList

    def heuristic(self, player, deadList):
        score = 0.0
        if deadList[0]:
            score = -math.inf
        elif True in deadList[1:]:
            score = math.inf
        else:
            # return float(self.snakes[player].health)
            # Only when health or length is less than certain threshold, give priority to food. Otherwise avoid food.
            needToLengthen = False
            for s in self.snakes:
                if s != self.snakes[player]:
                    if len(self.snakes[player].pos) < len(s.pos):
                        needToLengthen = True

            health = self.snakes[player].health
            length = float(len(self.snakes[player].pos))
            if health < 90 or needToLengthen:
                head = self.snakes[player].pos[0]
                minInvDist = -math.inf
                for food in self.foodList:
                    dist = abs(food.x-head.x) + abs(food.y-head.y)
                    invDist = 1.0 if dist == 0 else 1.0/float(dist)

                    for opponent_snake in self.snakes[1:]:
                        opponent_head = opponent_snake.pos[0]
                        opponent_dist = abs(
                            food.x - opponent_head.x) + abs(food.y - opponent_head.y)
                        if opponent_dist < 3:  # Adjust this threshold as needed
                            invDist /= 2  # Penalize moves towards this food
                            break

                    if minInvDist < invDist:
                        minInvDist = invDist
                    score = minInvDist + \
                        float(self.snakes[player].health)/100.0
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
        return (player+1) % n

    def minmaxMoveRecursive(self, depth, player, moveList0, moveList1, deadList, alpha=-math.inf, beta=math.inf):
        if depth == 0 or deadList[0] or deadList[1]:
            return (self.heuristic(player, deadList), None)
        if player == 0:
            bestScore = -math.inf
            bestMove = None
            for move in moveList0:
                newGame = self.moveSnake(player, move)
                newGameMoveList0 = newGame.moveOptions(player)
                newGameDeadList = newGame.checkDeadSnake(
                    [newGameMoveList0, moveList1])
                score = newGame.heuristic(player, newGameDeadList)
                if not newGameDeadList[0]:
                    # Penalize moves that result in head-to-head collisions
                    if len(newGame.snakes[player].pos) > 1 and len(newGame.snakes[1].pos) > 1:
                        if newGame.snakes[player].pos[1].x == newGame.snakes[1].pos[1].x and newGame.snakes[player].pos[1].y == newGame.snakes[1].pos[1].y:
                            score -= 100
                bestScore = max(bestScore, score)
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break
                if bestScore == score:
                    bestMove = move

                # if bestScore < score:
                    # bestScore = score
                    # bestMove = move
            return (bestScore, bestMove)
        else:
            bestScore = math.inf
            bestMove = None
            for move in moveList1:
                newGame = self.moveSnake(player, move)
                newGameMoveList1 = newGame.moveOptions(player)
                newGameDeadList = newGame.checkDeadSnake(
                    [moveList0, newGameMoveList1])
                score = newGame.heuristic(player, newGameDeadList)
                if not newGameDeadList[1]:
                    # Penalize moves that result in head-to-head collisions
                    if len(newGame.snakes[player].pos) > 1 and len(newGame.snakes[0].pos) > 1:
                        if newGame.snakes[player].pos[1].x == newGame.snakes[0].pos[1].x and newGame.snakes[player].pos[1].y == newGame.snakes[0].pos[1].y:
                            score += 100
                bestScore = min(bestScore, score)
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break
                if bestScore == score:
                    bestMove = move
                # if bestScore > score:
                    # bestScore = score
                    # bestMove = move
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

    if move == (-1, 0):
        return {"move": "left"}
    elif move == (1, 0):
        return {"move": "right"}
    elif move == (0, -1):
        return {"move": "down"}
    elif move == (0, 1):
        return {"move": "up"}
    else:
        return {"move": "up"}

    





# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})

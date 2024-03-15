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

import random
import typing
import sys
from collections import deque

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def find_closest_food(game_state: typing.Dict) -> typing.Dict:
    # Perform BFS to find the shortest path to the nearest food item
    board = game_state['board']
    head = game_state['you']['body'][0]
    visited = set()
    queue = deque([(head['x'], head['y'], 0)])
    
    while queue:
        x, y, dist = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if board['food'] and (x, y) in board['food']:
            return dist
        
        # Add adjacent cells to the queue
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < board['width'] and 0 <= ny < board['height'] and (nx, ny) not in visited:
                queue.append((nx, ny, dist + 1))
    
    # If no food found, return a large distance
    return float('inf')

def move(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

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

    # Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    if my_head["x"] == 0:  # Head is on the left edge
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:  # Head is on the right edge
        is_move_safe["right"] = False
    if my_head["y"] == 0:  # Head is on the top edge
        is_move_safe["up"] = False
    if my_head["y"] == board_height - 1:  # Head is on the bottom edge
        is_move_safe["down"] = False

    # Step 2 - Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body']
    for segment in my_body[1:]:  # Exclude head
        if segment['x'] == my_head['x'] and segment['y'] == my_head['y']:
            # The snake's head would collide with its body
            return {"move": "down"}  # Choose any safe move for now

    # Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']
    for snake in opponents:
        for segment in snake['body']:
            if segment['x'] == my_head['x'] and segment['y'] == my_head['y']:
                # The snake's head would collide with another snake's body
                return {"move": "down"}  # Choose any safe move for now

    # Step 4 - Move towards food instead of random, to regain health and survive longer
    food_distances = []
    for move, is_safe in is_move_safe.items():
        if is_safe:
            new_head = {'x': my_head['x'], 'y': my_head['y']}
            if move == 'up':
                new_head['y'] -= 1
            elif move == 'down':
                new_head['y'] += 1
            elif move == 'left':
                new_head['x'] -= 1
            elif move == 'right':
                new_head['x'] += 1
            dist_to_food = find_closest_food(game_state)
            food_distances.append((move, dist_to_food))

    # Sort by distance to food and choose the move with the shortest distance
    food_distances.sort(key=lambda x: x[1])
    closest_moves = [move[0] for move in food_distances if move[1] == food_distances[0][1]]

    # Choose a random move from the closest ones
    next_move = random.choice(closest_moves)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    port = "8000"
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == '--port':
            port = sys.argv[i+1]

    run_server({"info": info, "start": start, "move": move, "end": end, "port": port})

import random
import typing
import sys


def info() -> typing.Dict:
    return {
        "apiversion": "1",
        "author": "YourUsername",
        "color": "#888888",
        "head": "default",
        "tail": "default",
    }


def start(game_state: typing.Dict):
    pass


def end(game_state: typing.Dict):
    pass


def move(game_state: typing.Dict) -> typing.Dict:
    my_head = game_state["you"]["body"][0]
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # Prevent moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    if my_head['x'] == 0:
        is_move_safe["left"] = False
    elif my_head['x'] == board_width - 1:
        is_move_safe["right"] = False
    if my_head['y'] == 0:
        is_move_safe["down"] = False
    elif my_head['y'] == board_height - 1:
        is_move_safe["up"] = False

    # Prevent moving into self
    my_body = game_state['you']['body']
    for segment in my_body[1:]:
        if segment['x'] == my_head['x'] - 1 and segment['y'] == my_head['y']:
            is_move_safe["left"] = False
        elif segment['x'] == my_head['x'] + 1 and segment['y'] == my_head['y']:
            is_move_safe["right"] = False
        elif segment['y'] == my_head['y'] - 1 and segment['x'] == my_head['x']:
            is_move_safe["down"] = False
        elif segment['y'] == my_head['y'] + 1 and segment['x'] == my_head['x']:
            is_move_safe["up"] = False

    # Prevent moving into other snakes
    opponents = game_state['board']['snakes']
    for snake in opponents:
        for segment in snake['body']:
            if segment['x'] == my_head['x'] - 1 and segment['y'] == my_head['y']:
                is_move_safe["left"] = False
            elif segment['x'] == my_head['x'] + 1 and segment['y'] == my_head['y']:
                is_move_safe["right"] = False
            elif segment['y'] == my_head['y'] - 1 and segment['x'] == my_head['x']:
                is_move_safe["down"] = False
            elif segment['y'] == my_head['y'] + 1 and segment['x'] == my_head['x']:
                is_move_safe["up"] = False

    safe_moves = [move for move, safe in is_move_safe.items() if safe]

    # Move towards food
    next_move = move_towards_food(game_state, my_head)

    print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


def move_towards_food(game_state, my_head):
    board = game_state['board']
    food = board['food']

    closest_food = None
    min_distance = float('inf')

    for food_item in food:
        distance = abs(food_item['x'] - my_head['x']) + abs(food_item['y'] - my_head['y'])
        if distance < min_distance:
            min_distance = distance
            closest_food = food_item

    if closest_food:
        # Move towards the closest food item
        if closest_food['x'] > my_head['x']:
            return "right"
        elif closest_food['x'] < my_head['x']:
            return "left"
        elif closest_food['y'] > my_head['y']:
            return "up"
        elif closest_food['y'] < my_head['y']:
            return "down"
    
    # Default to a random move if no food is found
    return random.choice(["up", "down", "left", "right"])


if __name__ == "__main__":
    from server import run_server
    port = "8000"
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == '--port':
            port = sys.argv[i+1]

    run_server({"info": info, "start": start, "move": move, "end": end, "port": port})

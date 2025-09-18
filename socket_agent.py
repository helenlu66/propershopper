# Author: Gyan Tatiya
# Email: Gyan.Tatiya@tufts.edu

import json
import random
import socket

from env import SupermarketEnv
from utils import recv_socket_data

def step(sock_game, action: str):
    """Send an action to the game server and receive the response. Action can be the following:
    - NOP
    - NORTH
    - SOUTH
    - EAST
    - WEST
    - TOGGLE_CART
    - INTERACT

    Args:
        sock_game (socket.socket): The socket connection to the game server.
        action (str): The action to be performed in the game.
    """
    action = "0 " + action 
    sock_game.send(str.encode(action))  # send action to env
    output = recv_socket_data(sock_game)  # get observation from env
    # when the game ends, output will be empty bytes
    if output == b'':
        print("Game has ended.")
        return None
    output = json.loads(output)
    return output


if __name__ == "__main__":

    # Make the env
    # env_id = 'Supermarket-v0'
    # env = gym.make(env_id)

    action_commands = ['NOP', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TOGGLE_CART', 'INTERACT']

    print("action_commands: ", action_commands)

    # Connect to Supermarket
    HOST = '127.0.0.1'
    PORT = 9000
    sock_game = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_game.connect((HOST, PORT))

    output = step(sock_game, "NOP")
    print("Initial Observations: ", output["observation"])
    exit_pos = (0, 15.6)
    print("Exit position: ", exit_pos)

    while True:
        # action = str(random.randint(0, 1))
        # action += " " + random.choice(action_commands)  # random action

        agent_pos = output['observation']['players'][0]['position']
        cart_pos = output['observation']['cartReturns'][0]['position']
        has_cart = output['observation']['players'][0]['curr_cart'] != -1
        rel_dist_exit = (exit_pos[0] - agent_pos[0], exit_pos[1] - agent_pos[1])
        rel_dist_cart = (cart_pos[0] - agent_pos[0], cart_pos[1] - agent_pos[1])

        # Simple policy: if has cart, go to exit; else go to cart
        if has_cart:
            # first try to match y coordinate with exit, with 0.25 tolerance
            if abs(rel_dist_exit[1]) > 0.25:
                if rel_dist_exit[1] < 0:
                    action = "NORTH"
                else:
                    action = "SOUTH"
            else:
                if abs(rel_dist_exit[0]) > 0: # no tolerance here, need to go through the exit
                    if rel_dist_exit[0] < 0:
                        action = "WEST"
                    else:
                        action = "EAST"
        else:
            # first try to match x coordinate with cart, with 0.25 tolerance
            if abs(rel_dist_cart[0]) > 0.25:
                if rel_dist_cart[0] < 0:
                    action = "WEST"
                else:
                    action = "EAST"
            else:
                # then match y coordinate with cart, with 0.5 tolerance
                if abs(rel_dist_cart[1]) > 0.5:
                    if rel_dist_cart[1] < 0:
                        action = "NORTH"
                    else:
                        action = "SOUTH"
                else:
                    action = "INTERACT"  # pick up the cart
        # take action
        output = step(sock_game, action)

        print("Agent pos: ", agent_pos, " Has cart: ", has_cart, " Action: ", action)
        print("Violations", output["violations"])

from threading import Thread
import json

import ev3dev.ev3 as ev3

from ev3bt import ev3_server
import controller

class AuxController(Controller):
    def __init__(self, arg):
        super(, self).__init__()
        self.arg = arg



if __name__ == '__main__':
    # Initialize auxiliary brick, starts listening for commands
    robot = MainController('ev3_aux')

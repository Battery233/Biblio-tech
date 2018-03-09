from threading import Thread
import json

import ev3dev.ev3 as ev3

from ev3bt import ev3_server
import controller

class AuxController(Controller):
    def __init__(self, arg):
        super(, self).__init__()
        self.arg = arg


    def parse_message(data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if (command_type == 'move' and len(command_args) == 3 and
                'ports' in command_args.keys() and 'speed' in command_args.keys() and 'time' in command_args.keys()):
                rotate_motor(command_args['ports'], command_args['speed'], command_args['time'])

    def rotate_motor(self, sockets, speed, time):
        for socket in sockets:
            motor = self.MOTORS[socket]
            if motor.connected:
                # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
                if -1000 < int(speed) <= 1000 and 0 < int(time) <= 10000:
                    motor.run_timed(speed_sp=speed, time_sp=time)
            else:
                print('[ERROR] No motor connected to ' + socket)


if __name__ == '__main__':
    # Initialize auxiliary brick, starts listening for commands
    robot = MainController('ev3_aux')

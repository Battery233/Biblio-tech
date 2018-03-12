import json
from threading import Thread

import ev3dev.ev3 as ev3

from ev3bt import ev3_server

class Controller:
    MOTORS = [
        ev3.Motor('outA'),
        ev3.Motor('outB'),
        ev3.Motor('outC'),
        ev3.Motor('outD')
    ]

    def __init__(self, server_name):
        # Create bluetooth server and start it listening on a new thread
        server = ev3_server.BluetoothServer(server_name, self.parse_message)
        server_thread = Thread(target=server.start_server)
        server_thread.start()

    def parse_message(data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if (command_type == 'move' and len(command_args) == 3 and
                'ports' in command_args.keys() and 'speed' in command_args.keys() and 'time' in command_args.keys()):
                self.rotate_motor(command_args['ports'], command_args['speed'], command_args['time'])


    # Rotate motor
    # @param string socket  Output socket string (0 / 1 / 2 / 3)
    # @param int speed      Speed to rotate motor at (degrees/sec)
    # @param int time       Time to rotate motor for (milliseconds)
    def rotate_motor(self, sockets, speed, time):
        for socket in sockets:
            motor = self.MOTORS[socket]
            if motor.connected:
                # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
                if -1000 < int(speed) <= 1000 and 0 < int(time) <= 10000:
                    motor.run_timed(speed_sp=speed, time_sp=time)
            else:
                print('[ERROR] No motor connected to ' + socket)

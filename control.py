import json
import time

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

    def __init__(self, server_name=""):
        # Create bluetooth server and start it listening on a new thread

        if len(server_name) > 0:
            self.server = ev3_server.BluetoothServer(server_name, self.parse_message)
            self.server_thread = Thread(target=self.server.start_server)
            self.server_thread.start()

    def parse_message(self, data, socket):
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

    # Moves motor by specified distance at a certain speed and direction
    # @param int    socket     Socket index in MOTORS to use
    # @param float  dist       Distance to move motor in centimeters
    # @param int    speed      Speed to move motor at (degrees / sec)
    def move_motor_by_dist(self, motor, dist, speed, hold=False):
        if motor.connected:
            # convert to cm and then to deg
            angle = int(cm_to_deg(float(dist) / 10))
            if hold:
                motor.run_to_rel_pos(position_sp=angle, speed_sp=speed, stop_action='hold')
            else:
                motor.run_to_rel_pos(position_sp=angle, speed_sp=speed, )

            while not self.motor_ready(motor):
                time.sleep(0.1)
        else:
            print('[ERROR] No motor connected to ' + str(motor))

    def motor_ready(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        return motor.state != ['running']

import json
import time
from threading import Thread

import ev3dev.ev3 as ev3

from messages import client
from messages.server import Device

BRICK_VERTICAL_MOVEMENT = Device.BRICK_33
BRICK_HORIZONTAL_MOVEMENT = Device.BRICK_13
BRICK_BOOK_FETCHING = Device.BRICK_33


class Brick:
    MOTORS = [
        ev3.Motor('outA'),
        ev3.Motor('outB'),
        ev3.Motor('outC'),
        ev3.Motor('outD')
    ]

    def __init__(self, brick_id):
        self.stop_action = 'brake'
        self.client = client.BluetoothClient(brick_id, self.parse_message)
        client_thread = Thread(target=self.client.connect())
        client_thread.start()

    def send_message(self, socket, title, body=None):
        if body is not None:
            message = {title: body}
        else:
            message = {title: { } }
            # message = {'message': {"content": title}}

        print("sending message: " + json.dumps(message))
        socket.send(json.dumps(message))

    def parse_message(self, data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        # TODO: Add proper support for 'brick' param
        if (command_type == 'move' and len(command_args) == 4 and
                'ports' in command_args.keys() and 'speed'in command_args.keys() and 'brick' in command_args.keys() and 'time' in command_args.keys()):
            self.rotate_motor(map(self.letter_to_int, command_args['ports']), command_args['speed'], command_args['time'])

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
    def move_motor_by_dist(self, motor, dist, speed):
        if motor.connected:
            # convert to cm and then to deg
            angle = int(self.cm_to_deg(float(dist) / 10))
            motor.run_to_rel_pos(position_sp=angle, speed_sp=speed, stop_action=self.stop_action)

            self.wait_for_motor(motor)

        else:
            print('[ERROR] No motor connected to ' + str(motor))

    def motor_ready(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)

        # Motor is ready only when its state is empty according to documentation
        return motor.state == []

    def stop_motors(self, sockets=None):
        # Stop all the motors by default
        if sockets is None:
            sockets = [0, 1, 2, 3]
        for socket in sockets:
            m = self.MOTORS[socket]
            if m.connected:
                m.stop(stop_action=self.stop_action)

    def cm_to_deg(self, cm):
        DEG_PER_CM = 29.0323
        return DEG_PER_CM * cm

    def letter_to_int(self, letter):
        if letter == 'A':
            return 0
        elif letter == 'B':
            return 1
        elif letter == 'C':
            return 2
        elif letter == 'D':
            return 3
        elif isinstance(letter, int):
            return letter
        else:
            print("Set value to default A: value 0")
            return 0

    def wait_for_motor(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        while motor.state == ["running"]:
            print('Motor is still running')
            time.sleep(0.1)

#!/usr/bin/env python3

import json
import time

from ev3dev import ev3
from messages.server import Device

from brick import Brick
import control

HORIZONTAL_SOCKET = 0
HORIZONTAL_SPEED = 360

TOUCH_SENSOR_LEFT_ADDRESS = 'in1'
TOUCH_SENSOR_RIGHT_ADDRESS = 'in2'


class Brick13(Brick):

    def __init__(self, brick_id):
        super().__init__(brick_id)

        self.horizontal_motor = self.MOTORS[HORIZONTAL_SOCKET]

        self.touch_sensor_left = ev3.TouchSensor(address=TOUCH_SENSOR_LEFT_ADDRESS)
        self.touch_sensor_right = ev3.TouchSensor(address=TOUCH_SENSOR_RIGHT_ADDRESS)

        print('TouchSensor left connected? ' + str(self.touch_sensor_left.connected))
        print('TouchSensor right connected? ' + str(self.touch_sensor_right.connected))

        print('Stop action set to: ' + self.stop_action)

    def move(self, distance, socket):
        if not self.touch_sensor_left.connected or not self.touch_sensor_right.connected:
            print('Refusing to move: unsafe without touch sensors')
            return

        motor = self.horizontal_motor
        if motor.connected:
            # convert to cm and then to deg
            angle = int(self.cm_to_deg(float(distance) / 10))
            motor.run_to_rel_pos(position_sp=angle, speed_sp=HORIZONTAL_SPEED, )

        else:
            print('Horizontal motor not connected. Cannot move')

        while not self.motor_ready(motor):
            time.sleep(0.1)

            if self.touch_sensor_left.is_pressed:
                self.stop_motors([HORIZONTAL_SOCKET])
                print('Reached left edge! Stopping motors')
                self.send_message(socket, control.MESSAGE_LEFT_EDGE)
            if self.touch_sensor_right.is_pressed:
                self.stop_motors([HORIZONTAL_SOCKET])
                print('Reached right edge! Stopping motors')
                self.send_message(socket, control.MESSAGE_RIGHT_EDGE)

            time.sleep(0.1)

        self.send_message(socket, control.MESSAGE_SCAN_COMPLETE)

    def parse_message(self, data, socket):
        print("Parse message: " + data)

        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if (command_type == 'horizontal' and len(command_args) == 1 and
                'distance' in command_args.keys()):
            self.move(command_args['distance'], socket)

        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motors(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motors()
            else:
                raise ValueError('Invalid stop command')
        else:
            raise ValueError('Invalid command')


if __name__ == '__main__':
    # Initialize brick
    brick = Brick13(Device.RPI)

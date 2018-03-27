#!/usr/bin/env python3

import json
import time

from messages.server import Device

from brick import Brick
import control

VERTICAL_SOCKET_1 = 0
FINGER_SOCKET = 1
ARM_SOCKET = 2
VERTICAL_SOCKET_2 = 3

VERTICAL_MOVEMENT = 450
VERTICAL_SPEED = 250

ARM_TIME = 3200
ARM_EXTENSION_SPEED = -100
ARM_RETRACTION_SPEED = -ARM_EXTENSION_SPEED

FINGER_TIME = 1500
FINGER_EXTENSION_SPEED = 90
FINGER_RETRACTION_SPEED = -FINGER_EXTENSION_SPEED


class Brick33(Brick):

    def __init__(self, brick_id):
        super().__init__(brick_id)

        self.vertical_motor_1 = self.MOTORS[VERTICAL_SOCKET_1]
        self.vertical_motor_2 = self.MOTORS[VERTICAL_SOCKET_2]
        self.arm_motor = self.MOTORS[ARM_SOCKET]
        self.finger_motor = self.MOTORS[FINGER_SOCKET]

        self.stop_action = 'hold'

        print('Vertical motor 1 is: ' + str(self.vertical_motor_1))
        print('Vertical motor 2 is: ' + str(self.vertical_motor_2))
        print('Arm motor is: ' + str(self.arm_motor))
        print('Finger motor is: ' + str(self.finger_motor))
        print('Vertical motor 1 is connected?: ' + str(self.vertical_motor_1.connected))
        print('Vertical motor 2 is connected?: ' + str(self.vertical_motor_2.connected))
        print('Arm motor is connected?: ' + str(self.arm_motor.connected))
        print('Finger motor is connected?: ' + str(self.finger_motor.connected))

        print('Stop action set to: ' + self.stop_action)

    def parse_message(self, data, socket):
        print("Parse message: " + data)

        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if command_type == "up" and len(command_args) == 0:
            self.move_vertically(up=True)

        elif command_type == "down" and len(command_args) == 0:
            self.move_vertically(up=False)

        elif command_type == 'takeBook' and len(command_args) == 0:
            self.take_book()

        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motors(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motors()
            else:
                raise ValueError('Invalid stop command')

        else:
            raise ValueError('Invalid command')

    def move_vertically(self, up):
        # TODO: send busy message to RPI

        # "movement" has to be negative if moving up, positive if moving down
        if up:
            movement = VERTICAL_MOVEMENT
        else:
            movement = -VERTICAL_MOVEMENT

        print('Move by ' + str(movement))
        self.move_motor_by_dist(self.vertical_motor_1, movement, VERTICAL_SPEED)
        self.move_motor_by_dist(self.vertical_motor_2, movement, VERTICAL_SPEED)

        self.wait_for_motor(self.vertical_motor_1)
        self.wait_for_motor(self.vertical_motor_2)

        print("Movement successfully completed")

        # TODO: send available message to RPI

    def take_book(self):
        # TODO: send busy message to RPI

        print("Enter in take_book")
        # extend arm
        print("Move first motor")
        self.rotate_motor([ARM_SOCKET], ARM_EXTENSION_SPEED, ARM_TIME)

        print("wait 5 secs")
        time.sleep(5)  # TODO: check times later
        print("move second motor")
        # extend finger
        self.rotate_motor([FINGER_SOCKET], FINGER_EXTENSION_SPEED, FINGER_TIME)

        print("wait 5 secs again")
        time.sleep(5)
        print("move third motor")
        # retract arm
        self.rotate_motor([ARM_SOCKET], ARM_RETRACTION_SPEED, ARM_TIME)

        print("wait 5 secs for last time")
        time.sleep(5)
        print("move last motor")
        self.rotate_motor([FINGER_SOCKET], FINGER_RETRACTION_SPEED, FINGER_TIME)

        # TODO : send available message to RPI


if __name__ == '__main__':
    # Initialize brick
    brick = Brick33(Device.RPI)

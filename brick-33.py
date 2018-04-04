#!/usr/bin/env python3

import json
import time
from threading import Thread

from ev3dev import ev3
from messages.server import Device

from brick import Brick
import status

VERTICAL_SOCKET_1 = 0
FINGER_SOCKET = 1
ARM_SOCKET = 2
VERTICAL_SOCKET_2 = 3

VERTICAL_MOVEMENT = 625
VERTICAL_SPEED = 250

ARM_TIME = 3700
ARM_EXTENSION_SPEED = -100
ARM_RETRACTION_SPEED = -ARM_EXTENSION_SPEED

FINGER_TIME = 1800
FINGER_EXTENSION_SPEED = 90
FINGER_RETRACTION_SPEED = -FINGER_EXTENSION_SPEED

# flag for using vertical touch sensor or not
TOUCH_SENSOR_ENABLED = False
TOUCH_SENSOR_TOP_ADDRESS = 'in1'
TOUCH_SENSOR_BOTTOM_ADDRESS = 'in4'


class Brick33(Brick):

    def __init__(self, brick_id):
        super().__init__(brick_id)

        self.vertical_motor_1 = self.MOTORS[VERTICAL_SOCKET_1]
        self.vertical_motor_2 = self.MOTORS[VERTICAL_SOCKET_2]
        self.arm_motor = self.MOTORS[ARM_SOCKET]
        self.finger_motor = self.MOTORS[FINGER_SOCKET]

        if TOUCH_SENSOR_ENABLED:
            self.touch_sensor_TOP = ev3.TouchSensor(address=TOUCH_SENSOR_TOP_ADDRESS)
            self.touch_sensor_BOTTOM = ev3.TouchSensor(address=TOUCH_SENSOR_BOTTOM_ADDRESS)
            print('TouchSensor TOP connected? ' + str(self.touch_sensor_TOP.connected))
            print('TouchSensor BOTTOM connected? ' + str(self.touch_sensor_BOTTOM.connected))

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
            self.move_vertically(up=True, socket=socket)

        elif command_type == "down" and len(command_args) == 0:
            self.move_vertically(up=False, socket=socket)

        elif command_type == "enable_vertical_touch_sensor" and len(command_args) == 0:
            global TOUCH_SENSOR_ENABLED
            TOUCH_SENSOR_ENABLED = True

        elif command_type == 'takeBook' and len(command_args) == 0:
            self.take_book(socket)

        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motors(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motors()
            else:
                raise ValueError('Invalid stop command')

        else:
            raise ValueError('Invalid command')

    def move_vertically(self, up, socket):
        if TOUCH_SENSOR_ENABLED:
            if not self.touch_sensor_TOP.connected or not self.touch_sensor_BOTTOM.connected:
                print('Refusing to move: unsafe without vertical touch sensors')
                return


        # "movement" has to be negative if moving up, positive if moving down
        if up:
            movement = VERTICAL_MOVEMENT
        else:
            movement = -VERTICAL_MOVEMENT

        print('Move by ' + str(movement))
        thread_one = Thread(target=self.move_motor_by_dist, args=(self.vertical_motor_1, movement, VERTICAL_SPEED))
        thread_two = Thread(target=self.move_motor_by_dist, args=(self.vertical_motor_2, movement, VERTICAL_SPEED))
        thread_one.start()
        thread_two.start()

        # self.move_motor_by_dist(self.vertical_motor_1, movement, VERTICAL_SPEED)
        # self.move_motor_by_dist(self.vertical_motor_2, movement, VERTICAL_SPEED)

        if TOUCH_SENSOR_ENABLED:

            while not (self.motor_ready(self.vertical_motor_1) | self.motor_ready(self.vertical_motor_2)):

                if self.touch_sensor_TOP.is_pressed:
                    self.stop_motors(self.vertical_motor_1)
                    self.stop_motors(self.vertical_motor_2)

                    print('Reached TOP edge! Stopping motors')

                    self.send_message(socket, status.MESSAGE_TOP_EDGE)

                elif self.touch_sensor_BOTTOM.is_pressed:
                    self.stop_motors(self.vertical_motor_1)
                    self.stop_motors(self.vertical_motor_2)

                    print('Reached TOP edge! Stopping motors')

                    self.send_message(socket, status.MESSAGE_BOTTOM_EDGE)

                time.sleep(0.1)

        # TODO: test this wait action should be before while loop or after?
        self.wait_for_motor(self.vertical_motor_1)
        self.wait_for_motor(self.vertical_motor_2)

        print("Movement successfully completed")


    def take_book(self, socket):


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



if __name__ == '__main__':
    # Initialize brick
    brick = Brick33(Device.RPI)

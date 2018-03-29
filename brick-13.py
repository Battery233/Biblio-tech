#!/usr/bin/env python3

import json
import time

from ev3dev import ev3
from messages.server import Device

from brick import Brick
import status

HORIZONTAL_SOCKET = 0
HORIZONTAL_SPEED = 360
HORIZONTAL_SPEED_FOR_SCANNING = 30

TOUCH_SENSOR_LEFT_ADDRESS = 'in1'
TOUCH_SENSOR_RIGHT_ADDRESS = 'in2'

# move the robot to the left end when start
# make sure the touch sensor works or the whole thing will goes wrong
MOVE_TO_INITIAL_POSITION = False
START_FROM_LEFT = True
ROBOT_LENGTH = 170
RAILS_LENGTH = 705


class Brick13(Brick):

    def __init__(self, brick_id):
        super().__init__(brick_id)

        self.horizontal_motor = self.MOTORS[HORIZONTAL_SOCKET]

        self.touch_sensor_left = ev3.TouchSensor(address=TOUCH_SENSOR_LEFT_ADDRESS)
        self.touch_sensor_right = ev3.TouchSensor(address=TOUCH_SENSOR_RIGHT_ADDRESS)

        print('TouchSensor left connected? ' + str(self.touch_sensor_left.connected))
        print('TouchSensor right connected? ' + str(self.touch_sensor_right.connected))
        print('Stop action set to: ' + self.stop_action)

        if MOVE_TO_INITIAL_POSITION:
            if START_FROM_LEFT:
                if str(self.touch_sensor_left.connected):
                    print("move to very left position in 1 second")
                    time.sleep(1)
                    self.move(ROBOT_LENGTH - RAILS_LENGTH, [HORIZONTAL_SOCKET])
                    # make sure it will stop
                    self.stop_motors([HORIZONTAL_SOCKET])

                else:
                    print("Left touch sensor not ready")

            else:
                if str(self.touch_sensor_right.connected):
                    print("move to very right position in 1 second")
                    time.sleep(1)
                    self.move(RAILS_LENGTH - ROBOT_LENGTH, [HORIZONTAL_SOCKET])
                    print("get the position,set the position value to " + str(RAILS_LENGTH - ROBOT_LENGTH))
                    # make sure it will stop
                    self.stop_motors([HORIZONTAL_SOCKET])

                elif str(self.touch_sensor_left.connected):
                    print("Only left touch sensor is connected")

                else:
                    print("None of the  touch sensors are ready")

        else:
            print("Disabled moving to 0 position function")

    def move(self, distance, socket, scanning=False):
        if not self.touch_sensor_left.connected or not self.touch_sensor_right.connected:
            print('Refusing to move: unsafe without touch sensors')
            return

        self.send_message(socket, status.MESSAGE_BUSY, {'brick_id': Device.BRICK_13.value})

        motor = self.horizontal_motor
        if motor.connected:
            # convert to cm and then to deg
            angle = int(self.cm_to_deg(float(distance) / 10))
            if scanning:
                motor.run_to_rel_pos(position_sp=angle, speed_sp=HORIZONTAL_SPEED_FOR_SCANNING, )
            else:
                motor.run_to_rel_pos(position_sp=angle, speed_sp=HORIZONTAL_SPEED, )

        else:
            print('Horizontal motor not connected. Cannot move')

        while not self.motor_ready(motor):
            # We only care about the left sensor if we're moving left
            if distance > 0 and self.touch_sensor_left.is_pressed:
                self.stop_motors([HORIZONTAL_SOCKET])
                print('Reached left edge! Stopping motors')
                self.send_message(socket, status.MESSAGE_LEFT_EDGE)
            # Similarly, we only care about the right sensor if we're moving right
            if distance < 0 and self.touch_sensor_right.is_pressed:
                self.stop_motors([HORIZONTAL_SOCKET])
                print('Reached right edge! Stopping motors')
                self.send_message(socket, status.MESSAGE_RIGHT_EDGE)

            if self.touch_sensor_left.is_pressed:
                print('Touch sensor Left PRESSED')
            if self.touch_sensor_right.is_pressed:
                print('Touch sensor Right PRESSED')

            time.sleep(0.1)

        self.send_message(socket, status.MESSAGE_AVAILABLE, {'brick_id': Device.BRICK_13.value})

    def reset_position(self, socket):
        self.move(200000, socket)

    def parse_message(self, data, socket):
        print("Parse message: " + data)

        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if (command_type == 'horizontal' and len(command_args) == 1 and
                'amount' in command_args.keys()):
            self.move(command_args['amount'], socket)

        elif command_type == 'horizontal_scan' and len(command_args) == 1 and 'amount' in command_args.keys():
            self.move(command_args['amount'], socket, scanning=True)


        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motors(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motors()
            else:
                raise ValueError('Invalid stop command')

        elif command_type == status.MESSAGE_RESET_POSITION and len(command_args) == 0:
            self.reset_position(socket)

        elif command_type == status.MESSAGE_TOP_EDGE:
            print("Hit the TOP touch sensor")

        elif command_type == status.MESSAGE_BOTTOM_EDGE:
            print("Hit the BOTTOM touch sensor")

        else:
            raise ValueError('Invalid command')


if __name__ == '__main__':
    # Initialize brick
    brick = Brick13(Device.RPI)

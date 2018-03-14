import control
import json
from threading import Thread
import time
from ev3bt import ev3_client
from ev3bt.ev3_server import Device


class AuxController(control.Controller):
    VERTICAL_SOCKET_1 = 0
    FINGER_SOCKET = 1
    ARM_SOCKET = 2
    VERTICAL_SOCKET_2 = 3

    VERTICAL_MOTOR_1 = control.Controller.MOTORS[VERTICAL_SOCKET_1]
    VERTICAL_MOTOR_2 = control.Controller.MOTORS[VERTICAL_SOCKET_2]
    ARM_MOTOR = control.Controller.MOTORS[ARM_SOCKET]
    FINGER_MOTOR = control.Controller.MOTORS[FINGER_SOCKET]

    VERTICAL_MOVEMENT = 420
    VERTICAL_SPEED = 250

    ARM_TIME = 3200
    ARM_EXTENSION_SPEED = -100
    ARM_RETRACTION_SPEED = -ARM_EXTENSION_SPEED

    FINGER_TIME = 1500
    FINGER_EXTENSION_SPEED = 90
    FINGER_RETRACTION_SPEED = -FINGER_EXTENSION_SPEED

    def __init__(self):
        self.client = ev3_client.BluetoothClient(Device.OTHER_EV3, self.parse_message)
        client_thread = Thread()
        client_thread.start()

        super().__init__()
        
        print('Vertical motor 1 is: ' + str(self.VERTICAL_MOTOR_1))
        print('Vertical motor 2 is: ' + str(self.VERTICAL_MOTOR_2))
        print('Arm motor is: ' + str(self.ARM_MOTOR))
        print('Finger motor is: ' + str(self.FINGER_MOTOR))
        print('Vertical motor 1 is connected?: ' + str(self.VERTICAL_MOTOR_1.connected))
        print('Vertical motor 2 is connected?: ' + str(self.VERTICAL_MOTOR_2.connected))
        print('Arm motor is connected?: ' + str(self.ARM_MOTOR.connected))
        print('Finger motor is connected?: ' + str(self.FINGER_MOTOR.connected))

    def parse_message(self, data, socket):
        print("Parse message: " + data)
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if command_type == "up" and len(command_args) == 0:
            if self.move_vertically(up=True):
                self.send_message(socket, "vertical_success")
            else:
                self.send_message(socket, "vertical_failure")
        elif command_type == "down" and len(command_args) == 0:
            if self.move_vertically(up=False):
                self.send_message(socket, "vertical_success")
            else:
                self.send_message(socket, "vertical_failure")
        elif command_type == 'takeBook' and len(command_args) == 0:
            self.take_book()
        else:
            raise ValueError('Invalid command')

    def send_message(self, socket, title, body=None):
        # TODO: extract this method and put it into the parent class (remove it from main_brick.py as well)
        # generate message and send json file
        if body is not None:
            message = {title: body}
        else:
            message = {'message': {"content": title}}

        print("sending message: " + json.dumps(message))
        socket.send(json.dumps(message))

    def move_vertically(self, up):
        # "movement" has to be negative if moving up, positive if moving down
        if up:
            movement = self.VERTICAL_MOVEMENT
        else:
            movement = -self.VERTICAL_MOVEMENT
        
        print('Move by ' + str(movement))
        self.move_motor_by_dist(self.VERTICAL_MOTOR_1, movement, self.VERTICAL_SPEED, hold=True)
        self.move_motor_by_dist(self.VERTICAL_MOTOR_2, movement, self.VERTICAL_SPEED, hold=True)

        self.wait_for_motor(self.VERTICAL_MOTOR_1)
        self.wait_for_motor(self.VERTICAL_MOTOR_2)

        print("Movement successfully completed, return True")
        return True

    # TODO: maybe this must be @primary_action
    def take_book(self):
        print("Enter in take_book")
        # extend arm
        print("Move first motor")
        self.rotate_motor([self.ARM_SOCKET], self.ARM_EXTENSION_SPEED, self.ARM_TIME)

        print("wait 5 secs")
        time.sleep(5)  # TODO: check times later
        print("move second motor")
        # extend finger
        self.rotate_motor([self.FINGER_SOCKET], self.FINGER_EXTENSION_SPEED, self.FINGER_TIME)

        print("wait 5 secs again")
        time.sleep(5)
        print("move third motor")
        # retract arm
        self.rotate_motor([self.ARM_SOCKET], self.ARM_RETRACTION_SPEED, self.ARM_TIME)

        print("wait 5 secs for last time")
        time.sleep(5)
        print("move last motor")
        self.rotate_motor([self.FINGER_SOCKET], self.FINGER_RETRACTION_SPEED, self.FINGER_TIME)


if __name__ == '__main__':
    # Initialize auxiliary brick, starts listening for commands
    brick = AuxController()

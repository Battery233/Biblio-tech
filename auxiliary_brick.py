import control
import json
from threading import Thread
import time
from ev3bt import ev3_client
from ev3bt.ev3_server import Device


class AuxController(control.Controller):
    VERTICAL_SOCKET_1 = 0
    VERTICAL_SOCKET_2 = 1
    FINGER_SOCKET = 2
    ARM_SOCKET = 3

    VERTICAL_MOTOR_1 = control.Controller.MOTORS[VERTICAL_SOCKET_1]
    VERTICAL_MOTOR_2 = control.Controller.MOTORS[VERTICAL_SOCKET_2]
    ARM_MOTOR = control.Controller.MOTORS[ARM_SOCKET]
    FINGER_MOTOR = control.Controller.MOTORS[FINGER_SOCKET]

    VERTICAL_MOVEMENT = 180
    VERTICAL_SPEED = 45

    ARM_TIME = 2500
    ARM_EXTENSION_SPEED = -100
    ARM_RETRACTION_SPEED = -ARM_EXTENSION_SPEED

    FINGER_TIME = 1500
    FINGER_EXTENSION_SPEED = 90
    FINGER_RETRACTION_SPEED = -FINGER_EXTENSION_SPEED

    def __init__(self):
        self.client = ev3_client.BluetoothClient(Device.OTHER_EV3, self.parse_message)
        client_thread = Thread()
        client_thread.start()

        # Check if it is okay to assume that we always start from 0
        self.bottomRow = True

        super().__init__()

    def parse_message(self, data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if command_type == "up" and len(command_args) == 0:
            if self.move_vertically(up=True):
                self.send_message(socket, "vertical_success")
            else:
                self.send_message(socket, "vertical_failure")
        elif command_type == "down" and len(command_args) == 0:
            if self.move_vertically():
                self.send_message(socket, "vertical_success")
            else:
                self.send_message(socket, "vertical_failure")
        elif command_type == 'takeBook' and len(command_args) == 0:
            self.take_book(socket)
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
            if not self.bottomRow:
                print("Can't go up, we're already there")
                return False
            movement = -self.VERTICAL_MOVEMENT
        else:
            if self.bottomRow:
                print("Can't go down, we're already there")
                return False
            movement = self.VERTICAL_MOVEMENT

        self.move_motor_by_dist(self.VERTICAL_MOTOR_1, movement, self.VERTICAL_SPEED, hold=True)
        self.move_motor_by_dist(self.VERTICAL_MOTOR_2, movement, self.VERTICAL_SPEED, hold=True)

        self.wait_for_motor(self.VERTICAL_MOTOR_1)
        self.wait_for_motor(self.VERTICAL_MOTOR_2)

        # update position
        self.bottomRow = not self.bottomRow

        print("Movement successfully completed, return True")
        return True

    def wait_for_motor(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        while motor.state == ["running"]:
            print('Motor is still running')
            time.sleep(0.1)

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

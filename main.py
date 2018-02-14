from control import Controller
import vision.main as vision
import db.main as db
import ev3dev.ev3 as ev3

import json
import time
from threading import Thread


def startUp():
    # Turn camera on and get it as an object
    camera = vision.activate_camera()

    # Initialize controller and give it a camera
    robot = Controller(camera)

    # Stop all motors
    robot.stop_motor()

    # Position arm at the beginning of first cell
    robot.reachCell(0)

    # Check motors
    for i, motor in enumerate(control.MOTORS):
        if not motor.connected:
            print('Motor ' + i + ' non connected')

    # Create bluetooth server and start it listening on a new thread
    server = ev3_server.BluetoothServer("ev3 dev", parse_message)
    server_thread = Thread(target=server.start_server)
    server_thread.start()

def parse_message(data, socket):
    json_command = json.loads(data)

    command_type = list(json_command.keys())[0]
    command_args = json_command[command_type]

    if command_type == 'move' and len(command_args) == 3:
        move_motor(command_args['ports'], command_args['speed'], command_args['time'])
    elif command_type == 'stop':
        if len(command_args) == 1:
            stop_motor(command_args['ports'])
        else:
            stop_motor()
    elif command_type == 'reachBook' and len(command_args) == 1:
        # reach_book(command_args['ISBN'])
        pass
    elif command_type == 'takeBook' and len(command_args) == 0:
        # take_book()
        pass
    elif command_type == 'queryDB':
        if len(command_args) == 1:
            # query_DB(command_args['ISBN'])
            pass
        else:
            # query_DB()
            pass

    elif command_type == 'close':
        server.close_server()
        server_thread.join()
        sys.exit(0)

    elif command_type == 'ping':
        socket.send('pong')
    else:
        raise ValueError('Invalid command')

def queryDB(ISBN=None):
    pass

if __name__ == '__main__':
    startUp()

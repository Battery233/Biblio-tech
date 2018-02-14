#!/usr/bin/env python3
# dev_mode.py
# This is the script to be used in conjunction with the "dev mode" section of the app

import os
import sys
from threading import Thread
import ev3dev.ev3 as ev3
from ev3bt import ev3_server
import json

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


# Move motor
# @param string socket  Output socket string (outA / outB / outC / outD)
# @param int speed      Speed to move motor at (degrees/sec)
# @param int time       Time to move motor for (milliseconds)
def move_motor(socket, speed, time):
    motor = ev3.Motor(socket)
    if motor.connected:
        # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
        if -1000 < int(speed) <= 1000 and 0 < int(time) <= 10000:
            motor.run_timed(speed_sp=speed, time_sp=time)
    else:
        print('[ERROR] No motor connected to ' + socket)


def stop_motor(sockets=None):
    # Stop all the motors if nothing received
    if sockets is None:
        sockets = ['outA', 'outB', 'outC', 'outD']
    for socket in sockets:
        m = ev3.Motor(socket)
        if m.connected:
            m.stop(stop_action='brake')


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

# Create bluetooth server and start it listening on a new thread
server = ev3_server.BluetoothServer("ev3 dev", parse_message)
server_thread = Thread(target=server.start_server)
server_thread.start()

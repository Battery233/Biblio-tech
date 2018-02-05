#!/usr/bin/env python3
# dev_mode.py
# This is the script to be used in conjunction with the "dev mode" section of the app

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from ev3bt import ev3_bluetooth
import ev3dev.ev3 as ev3
from threading import Thread

# Get motor connected to output A
output_socket = 'outA'


# Move motor
# @param int speed  Speed to move motor at (degrees/sec)
# @param int time   Time to move motor for (milliseconds)
def move_motor(speed, time):
    motor = ev3.Motor(output_socket)
    if motor.connected:
        # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
        if -1000 < int(speed) <= 1000 and 0 < int(time) <= 10000:
            motor.run_timed(speed_sp=speed, time_sp=time)
    else:
        print('[ERROR] No motor connected to ' + output_socket)


def stop_motor():
    motor = ev3.Motor(output_socket)
    if motor.connected:
        motor.stop(stop_action='brake')
    else:
        print('[ERROR] Can\'t find motor connected to ' + output_socket + '. Uh oh.')


def parse_message(data, socket):
    parts = str(data).split(":")

    command = parts[0]

    if command == 'move' and len(parts) == 3:
        move_motor(parts[1], parts[2])

    elif command == 'stop':
        stop_motor()

    elif command == 'close':
        server.close_server()
        server_thread.join()
        sys.exit(0)

    elif command == 'ping':
        socket.send('pong')

    elif command == 'status':
        server.send_to_device("test", ev3_bluetooth.Device.OTHER_EV3)


# Create bluetooth server and start it listening on a new thread
server = ev3_bluetooth.BluetoothServer("ev3 dev", parse_message)
server_thread = Thread(target=server.start_server)
server_thread.start()

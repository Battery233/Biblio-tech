#!/usr/bin/env python3
# dev_mode.py
# This is the script to be used in conjunction with the "dev mode" section of the app

import os
import sys
from threading import Thread
import ev3dev.ev3 as ev3
from ev3bt import ev3_server

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


# Stops all connected motors
def stop_motor():
    for socket in ['outA', 'outB', 'outC', 'outD']:
        m = ev3.Motor(socket)
        if m.connected:
            m.stop(stop_action='brake')


def parse_message(data, socket):
    parts = str(data).split(":")

    command = parts[0]

    if command == 'move' and len(parts) == 4:
        move_motor(parts[1], parts[2], parts[3])

    elif command == 'stop':
        stop_motor()

    elif command == 'close':
        server.close_server()
        server_thread.join()
        sys.exit(0)

    elif command == 'ping':
        socket.send('pong')

    elif command == 'status':
        server.send_to_device("test", ev3_server.Device.OTHER_EV3)


# Create bluetooth server and start it listening on a new thread
server = ev3_server.BluetoothServer("ev3 dev", parse_message)
server_thread = Thread(target=server.start_server)
server_thread.start()

#!/usr/bin/env python3
# dev_mode.py
# This is the script to be used in conjunction with the "dev mode" section of the app

import json
import os
import sys
from threading import Thread

import ev3dev.ev3 as ev3

from ev3bt import ev3_server
from ev3bt.ev3_server import Device

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

MOTORS = [
    ev3.Motor('outA'),
    ev3.Motor('outB'),
    ev3.Motor('outC'),
    ev3.Motor('outD')
]

DEG_PER_CM = 29.0323


def detect_motors():
    global MOTORS
    MOTORS = [
        ev3.Motor('outA'),
        ev3.Motor('outB'),
        ev3.Motor('outC'),
        ev3.Motor('outD')
    ]


# Move motor
# @param string socket  Output socket string (outA / outB / outC / outD)
# @param int speed      Speed to move motor at (degrees/sec)
# @param int time       Time to move motor for (milliseconds)
def move_motor(socket, speed, time):
    detect_motors()
    motor = MOTORS[socket]
    if motor.connected:
        # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
        if -1000 < int(speed) <= 1000 and 0 < int(time) <= 10000:
            motor.run_timed(speed_sp=speed, time_sp=time)
    else:
        print('[ERROR] No motor connected to ' + str(motor))


# Moves motor by specified distance at a certain speed and direction
# @param int    socket     Socket index in MOTORS to use
# @param float  dist       Distance to move motor in centimeters
# @param int    speed      Speed to move motor at (degrees / sec)
def move_motor_by_dist(socket, dist, speed):
    detect_motors()
    motor = MOTORS[socket]

    if motor.connected:
        angle = cm_to_deg(dist)
        motor.run_to_rel_pos(position_sp=angle, speed_sp=int(speed))
    else:
        print('[ERROR] No motor connected to ' + str(motor))


def letter_to_int(letter):
    if letter == 'A':
        return 0
    elif letter == 'B':
        return 1
    elif letter == 'C':
        return 2
    elif letter == 'D':
        return 3
    else:
        return 0


# Stops all connected motors
def stop_motor():
    detect_motors()
    print("stop motors")
    for socket in ['outA', 'outB', 'outC', 'outD']:
        m = ev3.Motor(socket)
        if m.connected:
            m.stop(stop_action='brake')


def cm_to_deg(cm):
    return int(DEG_PER_CM * int(cm))


def parse_message(data, socket):
    valid_json = True

    try:
        json_command = json.loads(data)
        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]
    except:
        valid_json = False

    if valid_json:
        if command_type == 'move' and len(command_args) == 3:
            for port in command_args['ports']:
                motorPort = letter_to_int(port)
                move_motor(motorPort, command_args['speed'], command_args['time'])

        elif command_type == 'stop':
            stop_motor()

        if command_type == 'moveDist' and len(command_args) == 3:
            for port in command_args['ports']:
                motorPort = letter_to_int(port)
                move_motor_by_dist(motorPort, command_args['dist'], command_args['speed'])

    elif data == 'ping':
        socket.send('pong')

    elif data == 'status':
        server.send_to_device("hello", Device.OTHER_EV3)

    elif data == 'close':
        server.close_server()
        server_thread.join()
        sys.exit(0)


# Create bluetooth server and start it listening on a new thread
server = ev3_server.BluetoothServer("ev3 dev", parse_message)
server_thread = Thread(target=server.start_server)
server_thread.start()

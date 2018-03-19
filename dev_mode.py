#!/usr/bin/env python3
# dev_mode.py
# This is the script to be used in conjunction with the "dev mode" section of the app

import json
import os
import sys
from threading import Thread

import db.main as db
import ev3dev.ev3 as ev3

from messages import server

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

DB_FILE = db.PRODUCTION_DB

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


current_x_coordinateA = 0.0
current_x_coordinateB = 0.0
current_x_coordinateC = 0.0
current_x_coordinateD = 0.0


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
            motor.run_timed(speed_sp=speed, time_sp=time, stop_action='hold')
            global current_x_coordinateA
            global current_x_coordinateB
            global current_x_coordinateC
            global current_x_coordinateD
            if socket == 0:
                current_x_coordinateA += float(speed * time / 1000.0) / DEG_PER_CM
            elif socket == 1:
                current_x_coordinateB += float(speed * time / 1000.0) / DEG_PER_CM
            elif socket == 2:
                current_x_coordinateC += float(speed * time / 1000.0) / DEG_PER_CM
            elif socket == 3:
                current_x_coordinateD += float(speed * time / 1000.0) / DEG_PER_CM
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
        motor.run_to_rel_pos(position_sp=angle, speed_sp=int(speed), stop_action='hold')
        global current_x_coordinateA
        global current_x_coordinateB
        global current_x_coordinateC
        global current_x_coordinateD
        if socket == 0:
            current_x_coordinateA += dist
        elif socket == 1:
            current_x_coordinateB += dist
        elif socket == 2:
            current_x_coordinateC += dist
        elif socket == 3:
            current_x_coordinateD += dist

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


def query_DB(self, title=None):
    """
        If title is None, return a list of `(title, position)` for all the books
        in the database. Otherwise return a tuple of the form `(title, position)`
        for the title received as argument, or `None` if it is unavailable in the
        database.
        """

    if title is None:
        print("[query_DB], tittle is none")
        return db.get_books(DB_FILE)
    else:
        print("[query_DB], tittle is not none")
        return db.get_position_by_title(DB_FILE, title)


def send_message(self, socket, title, body=None):
    if body is not None:
        message = {title: body}
    else:
        message = {'message': {"content": title}}

    print("sending message: " + json.dumps(message))
    socket.send(json.dumps(message))


def parse_message(data, socket):
    valid_json = True

    try:
        json_command = json.loads(data)
        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]
    except:
        valid_json = False

    global current_x_coordinateA
    global current_x_coordinateB
    global current_x_coordinateC
    global current_x_coordinateD
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

        elif command_type == 'queryDB':
            '''
            The user might ask for the list of all books or for a specific book.

            If only a book is asked, then its position is searched in the database
            using the title. The message sent back to the app in this case is
            `bookItem` containing a tuple of `(title, position)` if the book is
            found or `None` otherwise.

            If all the books are requested, then the database is queried for all
            the books and their positions. The message sent back to the app in
            this case is `bookList` containing a list of `(title, position)`
            with all the books available.
            '''
            if len(command_args) == 1 and 'title' in command_args.keys():
                query_result = query_DB(command_args['title'])
                if query_result is not None:
                    args = (command_args['title'], query_result)
                else:
                    args = None
                send_message(socket, 'bookItem', args)
            elif len(command_args) == 0:
                print("[DBS in control.py]Give the book list of all books.")
                query_result = query_DB()
                built_query = []

                for i, book in enumerate(query_result):
                    book_dict = {'ISBN': query_result[i][0], 'title': query_result[i][1], 'author': query_result[i][2],
                                 'pos': int(query_result[i][3]), 'avail': query_result[i][4]}
                    built_query.append(book_dict)

                print(built_query)
                send_message(socket, 'bookList', built_query)
            else:
                raise ValueError('Invalid arguments for queryDB')

    elif data == 'ping':
        socket.send('pong')

    elif data == 'status':
        server.send_to_device("hello", Device.OTHER_EV3)

    elif data == 'coordinateA':
        print(current_x_coordinateA)
        socket.send(str(current_x_coordinateA))

    elif data == 'coordinateB':
        print(current_x_coordinateB)
        socket.send(str(current_x_coordinateB))

    elif data == 'coordinateC':
        print(current_x_coordinateC)
        socket.send(str(current_x_coordinateC))

    elif data == 'coordinateD':
        print(current_x_coordinateD)
        socket.send(str(current_x_coordinateD))

    elif data == 'clean':
        current_x_coordinateA = 0
        current_x_coordinateB = 0
        current_x_coordinateC = 0
        current_x_coordinateD = 0

    elif data == 'coordinate':
        socket.send("Use coordinateA to coordinateD")

    elif data == 'close':
        server.close_server()
        server_thread.join()
        sys.exit(0)


# Create bluetooth server and start it listening on a new thread
server = ev3_server.BluetoothServer("ev3 dev", parse_message)
server_thread = Thread(target=server.start_server)
server_thread.start()

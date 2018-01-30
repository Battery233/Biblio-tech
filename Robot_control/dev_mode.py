# dev_mode.py
# This is the script to be used in conjunction with the "dev mode" section of the app

from ev3bt.ev3_bluetooth import BluetoothServer
import ev3dev.ev3 as ev3
from threading import Thread

# Get motor connected to output A
output_socket = 'outA'
motor = ev3.Motor(output_socket)


# Move motor
# @param int speed  Speed to move motor at (degrees/sec)
# @param int time   Time to move motor for (milliseconds)
def move_motor(speed, time):
    if motor.connected:
        # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
        if -1000 < speed <= 1000 and 0 < time <= 10000:
            motor.run_timed(speed_sp=speed, time_sp=time)
    else:
        print('[ERROR] No motor connected to ' + output_socket)


def stop_motor():
    if motor.connected:
        motor.stop(stop_action='brake')
    else:
        print('[ERROR] Can\'t find motor connected to ' + output_socket + '. Uh oh.')


def parse_message(data):
    parts = str(data).split(":")

    command = parts[0]

    if command == 'move' and len(parts) == 3:
        move_motor(parts[1], parts[2])

    elif command == 'stop':
        stop_motor()

    elif command == 'close':
        server.close_server()

    elif command == 'ping':
        server.send('pong')


# Create bluetooth server and start it listening on a new thread
server = BluetoothServer("ev3 dev", parse_message)
server_thread = Thread(target=server.start_server)
server_thread.start()

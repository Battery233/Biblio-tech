# example.py
# This is an example of how to integrate the ev3_bluetooth.py
# module

from ev3_bluetooth import BluetoothServer
import ev3dev.ev3 as ev3
from threading import Thread


# Function that is called when from the bluetooth module  when it receives data
def on_received(data):
    # Motor connected to output socket 'A' of the EV3 brick
    m = ev3.Motor('outA')

    # To test sending messages (should make android phone vibrate)
    if data == 'ping':
        server.send('pong')

    # Move motor forward at speed 300 for 1 sec (1000ms = 1s)
    elif data == 'move':
        if not m.connected:
            print('ERROR: No motor is plugged in output A')
        else:
            m.run_timed(speed_sp=1000, time_sp=2880)

    # Move motor backwards at speed 300 for 1 sec (1000ms = 1s)
    elif data == 'reverse':
        if not m.connected:
            print('ERROR: No motor is plugged in output A')
        else:
            m.run_timed(speed_sp=-300, time_sp=1000)

    elif data == 'stop':
        server.close_server()


# Bluetooth server object that has been given a name "ev3 33" and the callback function has
# been set to the above function "on_received"
server = BluetoothServer("ev3 33", on_received)

# IMPORTANT: Must start the bluetooth server on a new thread otherwise it will block the current one
# target should the function you want to process the data the EV3 brick receives
thread = Thread(target=server.start_server)
thread.start()

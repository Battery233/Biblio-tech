#! /usr/bin/env python3

# Above line is needed for brick to be able to run script on its own

# Primitive script for handling bluetooth connections (one at most)
# Code adapted from: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py

from bluetooth import *
import ev3dev.ev3 as ev3

# Create server socket and listen
server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]

# UUID for connection (must be same on client, in our case the android app)
uuid = "00001101-0000-1000-8000-00805F9B34FB"

# Make socket visible to others
advertise_service(server_sock, "SampleServer", service_id=uuid)

print("Waiting for connection on RFCOMM channel %d" % port)

# Loop that keeps checking for new connections - only allows one at a time
while True:
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    # Motor connected to output socket 'A' of the EV3 brick
    m = ev3.Motor('outA')

    try:
        while True:

            data = client_sock.recv(1024)
            if len(data) == 0: break

            # Decodes bytes to string containing actual data (only needed in python3, works fine without in python2)
            data = data.decode("UTF-8")

            print("received [%s]" % data)

            # To test sending messages (should make android phone vibrate)
            if data == 'ping':
                client_sock.send('pong')

            # Move motor forward at speed 300 for 1 sec (1000ms = 1s)
            elif data == 'move':
                if not (m.connected):
                    print('plug motor into A')
                else:
                    m.run_timed(speed_sp=300, time_sp=1000)

            # Move motor backwards at speed 300 for 1 sec (1000 = 1s)
            elif data == 'reverse':
                if not (m.connected):
                    print('plug motor into A')
                else:
                    m.run_timed(speed_sp=-300, time_sp=1000)

    except IOError as e:
        # To handle
        pass


# Here so we remember they exist and can use them
# client_sock.close()
# server_sock.close()
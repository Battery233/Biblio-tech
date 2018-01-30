#! /usr/bin/env python3

# Above line is needed for brick to be able to run script on its own

# Primitive script for handling bluetooth connections (one at most)
# Code adapted from: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py

from bluetooth import *


class BluetoothServer:

    # UUID for connection (must be same on client, in our case the android app)
    uuid = "00001101-0000-1000-8000-00805F9B34FB"
    # Constructor for bluetooth server
    #
    # @param string name    Name of the server (doesn't really matter)
    # @param function name  Function to callback to when data is received (event handler basically)
    def __init__(self, name, callback):

        self.name = name
        self.callback = callback

        # Create server socket and listen
        self.server_sock = BluetoothSocket(RFCOMM)
        self.server_sock.bind(("", PORT_ANY))
        self.server_sock.listen(1)
        self.port = self.server_sock.getsockname()[1]
        self.should_run = True

    def __connection_loop__(self):

        # Loop that keeps checking for new connections - only allows one at a time by its structure
        while self.should_run:

            # Wait for connection (sever_sock.accept() blocks until it receives a connection)
            print("Waiting for connection on RFCOMM channel %d" % self.port)
            self.client_sock, client_info = self.server_sock.accept()

            # Connection received if we've reached this point
            print("Accepted connection from ", client_info)

            # Continually loop checking for incoming messages
            try:
                while True:

                    # Get bytes from client socket
                    data = self.client_sock.recv(1024)

                    # If we have received no data then break - exit while loop (i.e. don't progress to code below)
                    if len(data) == 0:
                        break

                    # Decodes bytes to string containing actual data (only needed in python3,
                    # works fine without in python2)
                    data = data.decode("UTF-8")

                    print("received [%s]" % data)

                    # Callback to function that was supplied
                    self.callback(data)

            except IOError as e:
                # Occurs when client disconnects
                print(e)
                self.client_sock.close()

    # Send data to client (Android app)
    def send(self, data):
        try:
            self.client_sock.send(data)
        except Exception as e:
            # To handle better hopefully
            print(e)

    # Start the server (this must be called for communication)
    def start_server(self):
        advertise_service(self.server_sock, self.name, self.uuid)
        self.__connection_loop__()

    # Close the server and
    def close_server(self):
        print('CLOSE SERVER')
        self.should_run = False
        self.client_sock.close()
        # self.server_sock.close()

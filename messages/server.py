#! /usr/bin/env python3

# Above line is needed for brick to be able to run script on its own

# Code adapted from: https://github.com/karulis/pybluez/blob/master/examples/simple/rfcomm-server.py

import json
import subprocess
from enum import Enum
from threading import Thread

from bluetooth import *

# MAC addresses of EV3 bricks
EV3_33_MAC = "B0:B4:48:76:E7:86"
EV3_13_MAC = "B0:B4:48:76:A2:C9"

# Message size (bytes)
MESSAGE_SIZE = 1024


class Device(Enum):
    RPI = 0
    BRICK_13 = 1
    BRICK_33 = 2
    APP = 3


# Class representing a bluetooth server, only ONE instance should be created
# as it can handle multiple connections
class BluetoothServer:
    # UUID for connection (must be same on client, in our case the android app and the other EV3 brick)
    uuid = "00001101-0000-1000-8000-00805F9B34FB"

    # Dictionary of clients { MAC (String) : Client socket {BluetoothSocket})
    clients = {}

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

        # Boolean used for while loops that check for connections/messages
        self.should_run = True

    # Loop for checking for messages sent from a client (called from __connection_loop)
    def __client_loop__(self, client_sock, client_info):
        try:
            while self.should_run:

                # Get bytes from client socket
                data = client_sock.recv(MESSAGE_SIZE)

                # If we have received no data then break - exit while loop (i.e. don't progress to code below)
                if len(data) == 0:
                    break

                # Decodes bytes to string containing actual data (only needed in python3,
                # works fine without in python2)
                data = data.decode("UTF-8")

                print("received [%s] \t from: %s" % (data, client_info[0]))

                # Callback to function that was supplied
                self.callback(data, client_sock)

        except IOError as e:
            # Occurs when client disconnects (usually)
            print(e)
            # Remove client from dictionary and close their socket
            self.clients.pop(client_info[0])
            client_sock.close()

    # Main loop essentially, checks for new connections and when it finds one
    # it creates a data receiving loop on a new thread
    def __connection_loop__(self):
        while self.should_run:
            # Wait for connection (sever_sock.accept() blocks until it receives a connection)
            print("Waiting for new connection on RFCOMM channel %d" % self.port)
            client_sock, client_info = self.server_sock.accept()

            # Connection received if we've reached this point
            print("Accepted connection from ", client_info)

            # Start message receiving loop for this client on a new thread
            t = Thread(target=self.__client_loop__, args=(client_sock, client_info))
            t.start()

            # Add newly connected client to dictionary of clients
            # client_info[0] is simply the MAC address string
            self.clients[client_info[0]] = client_sock

    # Extracts from the list of connected clients those with the type
    # we want (type defined using the Device enum)
    def __get_targets(self, device_type):
        targets = []

        if device_type == Device.BRICK_13 and EV3_13_MAC in self.clients.keys():
            targets.append(self.clients[EV3_13_MAC])
        elif device_type == Device.BRICK_33 and EV3_33_MAC in self.clients.keys():
            targets.append(self.clients[EV3_33_MAC])

        # This branch adds all of the connected app clients to the targets list - not useful currently
        # but it'll allow us in the future to send a message to all currently connected
        # app clients if needed
        elif device_type == Device.APP:
            for mac, client_socket in self.clients.items():
                # Add client only if it's not one of the bricks
                if mac != EV3_13_MAC and mac != EV3_33_MAC:
                    targets.append(client_socket)

        return targets

    # Prepare data to be sent to devices according to API
    def make_message(self, header, items=None, **kwargs):
        if (items is not None) > 0 and len(kwargs) > 0:
            raise ValueError('Cannot make a message with both a json array and a json object as body')

        if items is None:
            return json.dumps({header: kwargs})
        else:
            return json.dumps({header: items})

    # Send data to client
    # @param string data         Message to send
    # @param Device device_type  Type of client to send message to (Device enum defined above)
    def send_to_device(self, data, device_type):
        list_of_targets = self.__get_targets(device_type)

        if len(list_of_targets) > 0:
            for client in list_of_targets:
                try:
                    client.send(data)
                except Exception as e:
                    print(e)
        else:
            # This means no phones were connected if device_type = Device.APP or
            # the other brick wasn't connected if device_type = Device.OTHER_EV3
            print('No message sent! send_to_device() obtained an empty target list.')

    # Gets bluetooth MAC of the local device (brick we're running on)
    #
    # @return string    MAC address of this device
    def __get_local_mac(self):
        # Run shell command that outputs info about local bluetooth device
        cmd_output = subprocess.check_output(['hcitool', 'dev'])
        # Decode byte array to string
        cmd_output = cmd_output.decode('UTF-8')
        # Extract the last 18 characters (the MAC address)
        return cmd_output[-18:]

    # Start the server (this must be called for communication) and run event loop
    def start_server(self):
        advertise_service(self.server_sock, self.name, self.uuid)
        self.__connection_loop__()

    # Closes all client sockets in clients dictionary
    def __close_clients(self):
        for mac, client in self.clients.items():
            client.close()

    # @return True if both bricks connected to server, false otherwise
    def bricks_connected(self):
        return EV3_13_MAC in self.clients.keys() and EV3_33_MAC in self.clients.keys()

    # Close the server and clients
    def close_server(self):
        print('BLUETOOTH SERVER CLOSING')
        self.should_run = False
        self.__close_clients()
        self.server_sock.close()

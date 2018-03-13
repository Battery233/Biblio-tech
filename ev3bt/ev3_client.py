import subprocess
from threading import Thread

from bluetooth import *

from ev3bt.ev3_server import Device

MESSAGE_SIZE = 1024
uuid = "00001101-0000-1000-8000-00805F9B34FB"
EV3_33_MAC = "B0:B4:48:76:E7:86"
EV3_13_MAC = "B0:B4:48:76:A2:C9"
COLIN_MAC = "AC:FD:CE:2B:82:F1"


class BluetoothClient:

    # Constructor
    #
    # @param ev3_server.Device  Device type from ev3_server.Device enum
    # @param method             Method that handles received data (similar to ev3 server)
    def __init__(self, target, callback):
        self.target_addr = self.get_addr(target)
        self.callback = callback
        self.service_matches = find_service(uuid=uuid, address=self.target_addr)
        self.should_run = True

        if len(self.service_matches) > 0:
            self.first_match = self.service_matches[0]
            self.port = self.first_match['port']
            self.name = self.first_match['name']
            self.host = self.first_match['host']

            print("Connecting to \"%s\" on %s" % (self.name, self.host))

            # Create the client socket
            self.sock = BluetoothSocket(RFCOMM)
            self.sock.connect((self.host, self.port))

            print("Connected successfully!")

            self.recv_loop = Thread(target=self.receive_loop, args=(self.sock,))
            self.recv_loop.start()
        else:
            print('NO DEVICE FOUND')

    # Get the MAC address from the Device enum
    #
    # @return string    Mac address of other EV3
    def get_addr(self, device):
        local_mac = str(self.__get_local_mac()).strip()

        if device == Device.OTHER_EV3:
            if EV3_33_MAC == local_mac:
                return EV3_13_MAC
            else:
                return EV3_33_MAC
        else:
            return EV3_13_MAC

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

    def receive_loop(self, sock):
        while self.should_run:
            data = sock.recv(MESSAGE_SIZE)

            if len(data) == 0:
                break

            data = data.decode("UTF-8")
            self.callback(data, sock)

            print('Received: ' + str(data))

    def send_message(self, data):
        self.sock.send(data)

    def close_client(self):
        print("CLOSING CLIENT...")
        self.recv_loop.join()
        self.sock.close()
        sys.exit(0)
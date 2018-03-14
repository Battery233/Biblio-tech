from threading import Thread

from ev3bt import ev3_client
from ev3bt.ev3_server import Device


def parse_message(data, socket):
    print("==== parse message")
    # print(data)


client = ev3_client.BluetoothClient(Device.OTHER_EV3, parse_message)
client_thread = Thread()
client_thread.start()

client.send_message("test")


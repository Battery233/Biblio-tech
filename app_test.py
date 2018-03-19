from threading import Thread
from time import sleep

import json_list
from ev3bt import ev3_server


def avail(isbn):
    sleep(3)
    return False


def parse_message(data, socket):
    if str(data).startswith('{"queryDB'):
        socket.send(str(json_list.BOOKLIST))

    elif str(data).startswith('{"findBook'):
        isbn = str(data)[str(data).index("ISBN") + 7:-3]

        if avail(isbn):
            #socket.send('{"foundBook":{}}')
            socket.send('{"message":{"content":"foundBook"}}')
        else:
            #socket.send('{"missingBook":{}}')
            socket.send('{"message":{"content":"missingBook"}}')

# Create bluetooth server and start it listening on a new thread
server = ev3_server.BluetoothServer("ev3 dev", parse_message)
server_thread = Thread(target=server.start_server)
server_thread.start()

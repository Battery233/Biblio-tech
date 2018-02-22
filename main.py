from control import Controller
import vision.main as vision
import db.main as db
import ev3dev.ev3 as ev3

import json
import time
from threading import Thread


def startUp():
    # Turn camera on and get it as an object
    camera = vision.activate_camera()

    # Initialize controller and give it a camera
    robot = Controller(camera)

    # Stop all motors
    robot.stop_motor()

    # Position arm at the beginning of first cell
    robot.reachCell(0)

    # Check motors
    for i, motor in enumerate(control.MOTORS):
        if not motor.connected:
            print('Motor ' + i + ' non connected')

    # Create bluetooth server and start it listening on a new thread
    server = ev3_server.BluetoothServer("ev3 dev", parse_message)
    server_thread = Thread(target=server.start_server)
    server_thread.start()

def parse_message(data, socket):
    json_command = json.loads(data)

    command_type = list(json_command.keys())[0]
    command_args = json_command[command_type]

    if command_type == 'move' and len(command_args) == 3:
        move_motor(command_args['ports'], command_args['speed'], command_args['time'])
    elif command_type == 'stop':
        if len(command_args) == 1:
            stop_motor(command_args['ports'])
        else:
            stop_motor()
    elif command_type == 'findBook' and len(command_args) == 1:
		if not findBook(command_args['ISBN']):
			send_message('missingBook')
		else:
			send_message('foundBook')
    elif command_type == 'takeBook' and len(command_args) == 0:
        # take_book()
        pass
    elif command_type == 'queryDB':
		'''
		The user might ask for the list of all books or for a specific book.

		If only a book is asked, then its position is searched in the database
		using the title. The message sent back to the app in this case is
		`bookItem` containing a tuple of `(title, position)` if the book is
		found or `None` otherwise.

		If all the books are requested, then the database is queried for all
		the books and their positions. The mesage sent back to the app in 
		this case is `bookList` containing a list of `(title, position)`
		with all the books available.
		'''
        if len(command_args) == 1:
            query_result = query_DB(command_args['title'])
			if query_result is not None:
				args = (title, query_result)
			else:
				args = None
			send_message('bookItem', args)
        else:
            query_result = query_DB()
			send_message('bookList', query_result)

    elif command_type == 'close':
        server.close_server()
        server_thread.join()
        sys.exit(0)

    elif command_type == 'ping':
        socket.send('pong')
    else:
        raise ValueError('Invalid command')

def query_DB(title=None):
	'''
	If title is None, return a list of `(title, position)` for all the books
	in the database. Otherwise return a tuple of the form `(title, position)`
	for the title received as argument, or `None` if it is unavailable in the
	database.
	'''
	
	if title is None:
		return db.get_books()
	else:
		return db.get_position_by_title(title)

if __name__ == '__main__':
    startUp()

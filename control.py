import db.main as db
import vision.main as vision

import time
import json
from threading import Thread

import ev3dev.ev3 as ev3

class Controller:

    INITIAL_STATE = {'alignedToBook': None}

    MOTORS = [
        ev3.Motor('outA'),
        ev3.Motor('outB'),
        ev3.Motor('outC'),
        ev3.Motor('outD')
        ]

    CELLS_START = [(0,0), (500,0), (0,500), (500,500)]
    TOLERABLE_OFFSET = 5

    def __init__(self):
        # Initialize robot's internal model
        self.state = self.INITIAL_STATE

        # Turn camera on and get it as object
        self.camera = vision.activate_camera()

        # Stop all motors
        robot.stop_motor()

        # Position arm at the beginning of first cell
        robot.reachCell(0)

        # Check motors
        for i, motor in enumerate(control.MOTORS):
            if not motor.connected:
                print('Motor ' + i + ' non connected')

        # Create bluetooth server and start it listening on a new thread
        self.server = ev3_server.BluetoothServer("ev3 dev", self.parse_message)
        self.server_thread = Thread(target=server.start_server)
        self.server_thread.start()

    def reach_cell(self, cell):
        # do some movement
        self.wait_for_motor(motor)
        self.state['position'] = CELLS[cell]

    def scan_ISBN(self, ISBN):
        # start horizontal movement needed to almost reach next cell

        while(not self.motor_ready(motor)):
            decoded_ISBN, offset = vision.read_QR(self.camera)
            if ISBN == decoded_ISBN and offset < TOLERABLE_OFFSET:
                self.stop_motor()
                return True
            time.sleep(0.1)

        return False


    def find_book(self, title):
		'''
		Move the robot at the position of the book having the title received
		as an argument.
		'''
        cell = db.get_position_by_title(title)
		if cell is None:
			print('Book does not exist')
			return

        self.reachCell(cell)
		ISBN = db.get_ISBN_by_title(title)
        if not self.scan_ISBN(ISBN):
            self.send_message('missingBook')
            # self.full_scan(ISBN) if requested by app
    	else:
            self.state['alignedToBook'] = ISBN
    		self.send_message('foundBook')

    def take_book(self):
        if self.state['alignedToBook'] is not None:
            # do some movement
            pass
        else:
            # send some error message
            pass

    def full_scan(self, ISBN):
        pass

    def wait_for_motor(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        while motor.state==["running"]:
            print('Motor is still running')
            time.sleep(0.1)

    def motor_ready(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        return motor.state != ['running']

    # Move motor
    # @param string socket  Output socket string (0 / 1 / 2 / 3)
    # @param int speed      Speed to move motor at (degrees/sec)
    # @param int time       Time to move motor for (milliseconds)
    def move_motor(self, socket, speed, time):
        motor = self.MOTORS[socket]
        if motor.connected:
            # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
            if -1000 < int(speed) <= 1000 and 0 < int(time) <= 10000:
                motor.run_timed(speed_sp=speed, time_sp=time)
        else:
            print('[ERROR] No motor connected to ' + socket)

    def stop_motor(self, sockets=None):
        # Stop all the motors by default
        if sockets is None:
            sockets = [0, 1, 2, 3]
        for socket in sockets:
            m = self.MOTORS[socket]
            if m.connected:
                m.stop(stop_action='brake')

    def parse_message(self, data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if command_type == 'move' and len(command_args) == 3:
            self.move_motor(command_args['ports'], command_args['speed'], command_args['time'])
        elif command_type == 'stop':
            if len(command_args) == 1:
                self.stop_motor(command_args['ports'])
            else:
                self.stop_motor()
        elif command_type == 'findBook' and len(command_args) == 1:
            self.find_book(command_args['ISBN']):
    	elif command_type == 'takeBook' and len(command_args) == 0:
            self.take_book()
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
                query_result = self.query_DB(command_args['title'])
    			if query_result is not None:
    				args = (title, query_result)
    			else:
    				args = None
    			self.send_message('bookItem', args)
            else:
                query_result = self.query_DB()
    			self.send_message(socket, 'bookList', query_result)

        elif command_type == 'close':
            self.server.close_server()
            self.server_thread.join()
            sys.exit(0)

        elif command_type == 'ping':
            socket.send('pong')
        else:
            raise ValueError('Invalid command')

    def send_message(self, socket, title, body=None):
        # TODO: fix nonsensical API
        if body is not None:
            message = {'title': query_result}
        else:
            message = {'message': title}

        socket.send(json.dumps(message))

    def query_DB(self, title=None):
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
    # Initialize robot, starts listening for commands
    robot = Controller()

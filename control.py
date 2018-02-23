import db.main as db
import vision.main as vision

import time
import json
from threading import Thread

import ev3dev.ev3 as ev3

def primary_action(action):
    '''
    Method decorator to check whether robot is busy with some other operation
    before having it start a new action, and to prevent other actions from
    starting
    '''
    def safety_wrapper(self, socket, *args, **kwargs):
        # If state is already busy trying to change it will return False
        if not self.state_wait():
            self.send_busy_message(socket)
            return

        # If any of the motors is busy, robot is busy
        for motor in self.MOTORS:
            if not self.motor_ready(motor):
                self.send_busy_message(socket)
                return

        # Perform the action described by the method
        action(self, *args, **kwargs)

        # Free the robot
        self.state_signal()

    return safety_wrapper

class Controller:

    INITIAL_STATE = {'alignedToBook': None, 'busy': False}

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
        self.stop_motor()

        # Position arm at the beginning of first cell
        self.reachCell(0)

        # Check motors
        for i, motor in enumerate(self.MOTORS):
            if not motor.connected:
                print('Motor ' + i + ' non connected')

        # Create bluetooth server and start it listening on a new thread
        self.server = ev3_server.BluetoothServer("ev3 dev", self.parse_message)
        self.server_thread = Thread(target=server.start_server)
        self.server_thread.start()

    def state_wait(self):
        if self.state['busy']:
            return False
        else:
            self.state['busy'] = True
            return True

    def state_signal(self):
        self.state['busy'] = False

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

    @primary_action
    def find_book(self, socket, title):
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
            self.send_message(socket, 'missingBook')
            # self.full_scan(ISBN) if requested by app
    	else:
            self.state['alignedToBook'] = ISBN
    		self.send_message(socket, 'foundBook')

    @primary_action
    def take_book(self, socket):
        if self.state['alignedToBook'] is not None:
            # do some movement
            pass
        else:
            # send some error message
            pass

    @primary_action
    def full_scan(self, socket, ISBN):
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

        if command_type == 'move' and len(command_args) == 3 and
            ('ports' in command_args.keys() and
                'speed' in command_args.keys() and
                'time' in command_args.keys()):
            self.move_motor(command_args['ports'], command_args['speed'], command_args['time'])

        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motor(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motor()
            else:
                raise ValueError('Invalid command')

        elif command_type == 'findBook' and len(command_args) == 1
            and ('ISBN' in command_args.keys):
            self.find_book(socket, command_args['ISBN']):

        elif command_type == 'fullScan' and len(command_args) == 1
            and ('ISBN' in command_args.keys):
            self.full_scan(socket, command_args['ISBN']):

    	elif command_type == 'takeBook' and len(command_args) == 0:
            self.take_book(socket)

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
            if len(command_args) == 1 and ('title' in command_args.keys()):
                query_result = self.query_DB(command_args['title'])
    			if query_result is not None:
    				args = (title, query_result)
    			else:
    				args = None
    			self.send_message(socket, 'bookItem', args)
            elif len(command_args) == 0:
                query_result = self.query_DB()
    			self.send_message(socket, 'bookList', query_result)
            else:
                raise ValueError('Invalid arguments for queryDB')

        elif command_type == 'close':
            self.server.close_server()
            self.server_thread.join()
            sys.exit(0)

        elif command_type == 'ping':
            socket.send('pong')

        else:
            raise ValueError('Invalid command')

    def send_message(self, socket, title, body=None):
        if body is not None:
            message = {title: body}
        else:
            message = {'message': title}

        socket.send(json.dumps(message))

    def send_busy_message(self, socket):
        self.send_message(socket, 'busy')

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

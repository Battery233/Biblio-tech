import json
import sys
import time
from threading import Thread

import db.main as db
import vision.main as vision
from messages.server import Device

BRICK_VERTICAL_MOVEMENT = Device.BRICK_33
BRICK_HORIZONTAL_MOVEMENT = Device.BRICK_13
BRICK_BOOK_FETCHING = Device.BRICK_33


# FOR HARCODE:
IGNORE_QR_CODE = False

WEALTH_OF_NATIONS_ISBN = 9781840226881
THE_CASTLE_ISBN = 9780241197806

DB_FILE = db.PRODUCTION_DB


def primary_action(action):
    """
    Method decorator to check whether robot is busy with some other operation
    before having it start a new action, and to prevent other actions from
    starting
    """

    def safety_wrapper(self, socket, *args, **kwargs):
        # If state is already busy trying to change it will return False
        if not self.wait():
            self.send_busy_message(socket)
            print('Robot was busy and was not able to perform action')
            return

        # Perform the action described by the method
        action(self, socket, *args, **kwargs)

        # Free the robot
        self.signal()

    return safety_wrapper

def disruptive_action(action):
    def break_get_book_flow(self, socket, *args, **kwargs):
        # Break the flow of findBook - takeBook. Sorry user, too slow
        self.state['alignedToBook'] = None

        action(self, socket, *args, **kwargs)

    return break_get_book_flow


class Robot():
    ROBOT_LENGTH = 170  # TODO: compute this again
    RAILS_LENGTH = 705  # TODO: compute this again

    BOOK_WIDTH = 60
    CELL_WIDTH = 210
    END_CELL_OFFSET = 10
    CELLS_START = [0, CELL_WIDTH, 0, CELL_WIDTH]  # Bottom level, left to right, top level, left to right
    CELLS_END = [CELL_WIDTH - BOOK_WIDTH - END_CELL_OFFSET,  # Bottom level, left cell
                 2 * CELL_WIDTH - BOOK_WIDTH - END_CELL_OFFSET,  # Bottom level, right cell
                 CELL_WIDTH - BOOK_WIDTH - END_CELL_OFFSET,  # Top level, left cell
                 500 - BOOK_WIDTH - END_CELL_OFFSET, 300]  # Top level, right cell

    MESSAGE_BOOK_NOT_ALIGNED = 'bookNotAligned'
    MESSAGE_BUSY = 'busy'
    MESSAGE_MISSING_BOOK = 'missingBook'
    MESSAGE_FOUND_BOOK = 'foundBook'

    def __init__(self, server_name):
        # Create sample production.db in root folder
        db.flush_db(DB_FILE)
        db.create_book_table(DB_FILE)
        db.add_sample_books(DB_FILE)

        # Initialize robot's x_coordinate to 0 (TODO: get rid of this assumption?):
        self.current_x_coordinate = 0
        # Initialize robot's vertical position to be the bottom row: (TODO: check if we can get rid of this assumption)
        self.bottom_row = True
        self.aligned_to_book = None
        self.is_busy = False

        # Turn camera on and get it as object
        self.camera = vision.activate_camera()

        # Stop all motors
        self.stop_motors()

        if not self.TOUCH_SENSOR.connected:
            print("Unsafe! Touch sensor not connected")

        # Move the robot at the beginning of first cell
        self.reach_cell(0)

        # Create bluetooth server and start it listening on a new thread
        self.server = messages.server.BluetoothServer(server_name, self.parse_message)
        self.server_thread = Thread(target=self.server.start_server)
        self.server_thread.start()

    def wait(self):
        if self.is_busy:
            return False
        else:
            self.is_busy = True
            print('Initiating action, robot is now busy')
            return True

    def signal(self):
        self.is_busy = False
        print('Ending action, freeing robot')

    def reach_cell(self, cell, end_of_cell=False):
        # Get the target x coordinate (the place where we want to move the robot)

        if end_of_cell:
            target_x_coordinate = self.CELLS_END[cell]
        else:
            target_x_coordinate = self.CELLS_START[cell]

        # Compute the offset with which the robot will be moved
        # x_offset = target_x_coordinate - self.current_x_coordinate
        x_offset = self.current_x_coordinate - target_x_coordinate

        if cell > 1 and self.bottom_row:
            # If the index is in the second half, this cell is on the upper row...:)
            print("Move the robot by " + str(x_offset))
            if x_offset >= 0:
                action = 'right'
                distance = x_offset
            else:
                action = 'left'
                distance = abs(x_offset)
            args = {'move': distance}

            message = messages.make_message(action, distance=distance)
            self.server.send_to_device(message, BRICK_HORIZONTAL_MOVEMENT)

            self.server.send_to_device(messages.make_message('up'), BRICK_VERTICAL_MOVEMENT)
            time.sleep(8)
            self.bottom_row = False

        elif cell <= 1 and not self.bottom_row:
            message = '{"down":{}}'
            self.server.send_to_device(message, BRICK_VERTICAL_MOVEMENT)
            time.sleep(8)
            self.bottom_row = True

            print("Move the robot by " + str(x_offset))
            if x_offset >= 0:
                action = 'right'
                distance = x_offset
            else:
                action = 'left'
                distance = abs(x_offset)
            args = {'move': distance}

            message = messages.make_message(action, distance=distance)
            self.server.send_to_device(message, BRICK_HORIZONTAL_MOVEMENT)

        # Update the current x_coordinate to be the target coordinate as the robot is now there
        self.current_x_coordinate = target_x_coordinate

        print("[reach_cell]: waiting for motor to free")
        # TODO: Change this to wait for the brick's response instead of harcoded sleeping
        time.sleep(10)
        # self.wait_for_motor(self.HORIZONTAL_MOTOR)
        print("[reach_cell]: action complete")

    def scan_ISBN(self, ISBN):
        print("Scanning for ISBN " + ISBN)

        while not self.motor_ready(self.HORIZONTAL_MOTOR):
            decoded_ISBN, offset = vision.read_QR(self.camera)
            if ISBN == decoded_ISBN and offset < self.TOLERABLE_OFFSET:
                self.stop_motor()
                return True

        return False

    @primary_action
    @disruptive_action
    def find_book(self, socket, ISBN):
        '''
        Move the robot at the position of the book having the title received
        as an argument.
        '''

        print("The received ISBN is " + str(ISBN))

        # The received ISBN is a string so we make it an int
        # TODO: this must be updated to properly retrieve the book's position from the database, not hardcoded.
        end_of_cell = False
        if int(ISBN) == WEALTH_OF_NATIONS_ISBN:
            print("The searched book is Wealth of Nations")
            # Need to reach the end of cell 0 (so the beginning of cell 1)
            cell = 0
            end_of_cell = False
        elif int(ISBN) == THE_CASTLE_ISBN:
            print("The searched book is The Castle")
            # Need to reach the end of cell 1 (so the beginning of cell 2 - actually the end of the rails)
            cell = 1
            end_of_cell = False

        else:
            cell = int(db.get_position_by_ISBN(DB_FILE, ISBN))
            end_of_cell = False

        print(cell)

        self.reach_cell(cell, end_of_cell)

        # TODO: current ignore wiggling and qr recognize on top shelf
        global IGNORE_QR_CODE
        if self.bottom_row:
            IGNORE_QR_CODE = False
        else:
            IGNORE_QR_CODE = True
        print("Ignore QR code? : " + str(IGNORE_QR_CODE))
        # if IGNORE_QR_CODE is true, then don't scan the QR code and just assume the book is the right one
        if IGNORE_QR_CODE or self.scan_ISBN(ISBN):
            self.aligned_to_book = ISBN
            print("[FindBook] sending message: book found")
            self.send_message(socket, self.MESSAGE_FOUND_BOOK)
        else:
            self.send_message(socket, self.MESSAGE_MISSING_BOOK)

    @primary_action
    @disruptive_action
    def full_scan(self, socket, ISBN):
        # TODO: A LOT
        pass

    def stop_motors(self, ports=None):
        # Currrently, ignores the 'ports' argument for simplicity
        message = self.server.make_message('stop')
        for device in Device:
            self.server.send_to_device(message, device)


    def parse_message(self, data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        if (command_type == 'move' and len(command_args) == 3 and
                'ports' in command_args.keys() and 'speed' in command_args.keys() and 'time' in command_args.keys()):
            self.rotate_motor(command_args['ports'], command_args['speed'], command_args['time'])

        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motors(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motors()
            else:
                raise ValueError('Invalid command')

        elif command_type == 'findBook' and len(command_args) == 1 and 'ISBN' in command_args.keys():
            self.find_book(socket, command_args['ISBN'])

        elif command_type == 'fullScan' and len(command_args) == 1 and 'ISBN' in command_args.keys():
            self.full_scan(socket, command_args['ISBN'])

        elif command_type == 'takeBook' and len(command_args) == 1:
            ISBN = command_args['ISBN']
            if self.aligned_to_book == ISBN:
                message = '{"takeBook":{}}'
                self.server.send_to_device(message, BRICK_BOOK_FETCHING)
                time.sleep(23)
                self.reach_cell(0)
            else:
                self.send_message(socket, self.MESSAGE_BOOK_NOT_ALIGNED)

        elif command_type == 'queryDB':
            '''
            The user might ask for the list of all books or for a specific book.

            If only a book is asked, then its position is searched in the database
            using the title. The message sent back to the app in this case is
            `bookItem` containing a tuple of `(title, position)` if the book is
            found or `None` otherwise.

            If all the books are requested, then the database is queried for all
            the books and their positions. The message sent back to the app in
            this case is `bookList` containing a list of `(title, position)`
            with all the books available.
            '''
            if len(command_args) == 0:
                query_result = self.query_DB()
                built_query = []

                for i, book in enumerate(query_result):
                    book_dict = {
                        'ISBN': query_result[i][0],
                        'title': query_result[i][1],
                        'author': query_result[i][2],
                        'pos': int(query_result[i][3]),
                        'avail': query_result[i][4]
                    }
                    built_query.append(book_dict)

                print(built_query)
                self.send_message(socket, 'bookList', items=built_query)
            else:
                raise ValueError('Invalid arguments for queryDB')

        elif command_type == 'close':
            self.server.close_server()
            self.server_thread.join()
            sys.exit(0)

        elif command_type == 'ping':
            socket.send('pong')

        elif command_type == 'vertical_success':
            print('Started vertical movement')

        elif command_type == 'vertical_failure':
            print('Could not perform vertical movement: already up or already down')

    def send_busy_message(self, socket):
        self.send_message(socket, self.MESSAGE_BUSY)

    def query_DB(self, title=None):
        """
        If title is None, return a list of `(title, position)` for all the books
        in the database. Otherwise return a tuple of the form `(title, position)`
        for the title received as argument, or `None` if it is unavailable in the
        database.
        """

        if title is None:
            print("[query_DB], tittle is none")
            return db.get_books(DB_FILE)
        else:
            print("[query_DB], tittle is not none")
            return db.get_position_by_title(DB_FILE, title)



if __name__ == '__main__':
    # Initialize robot, starts listening for commands
    robot = Robot('raspberry-pi')

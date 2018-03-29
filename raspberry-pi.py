import json
import sys
import time
from threading import Thread

import db.main as db
import vision.main as vision
import status
from messages import server
from messages.server import Device

BRICK_VERTICAL_MOVEMENT = Device.BRICK_33
BRICK_HORIZONTAL_MOVEMENT = Device.BRICK_13
BRICK_BOOK_FETCHING = Device.BRICK_33

# FOR HARDCODE:
IGNORE_QR_CODE = False

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
        # self.state['alignedToBook'] = None
        self.aligned_to_book = None

        action(self, socket, *args, **kwargs)

    return break_get_book_flow


class Robot:
    # TODO: compute these again
    ROBOT_LENGTH = 170
    RAILS_LENGTH = 705
    ROBOT_RIGHT_COORDINATE = RAILS_LENGTH - ROBOT_LENGTH

    BOOK_WIDTH = 60
    # (former) CELL_WIDTH = 210
    CELL_WIDTH = 105
    CELLS_PER_ROW = 4

    TOLERABLE_OFFSET = 5  # mm

    MESSAGE_BOOK_NOT_ALIGNED = 'bookNotAligned'
    MESSAGE_BUSY = 'busy'
    MESSAGE_MISSING_BOOK = 'missingBook'
    MESSAGE_FOUND_BOOK = 'foundBook'

    BRICK_AVAILABLE_STATE = 'available'
    BRICK_BUSY_STATE = 'busy'

    scanning_over = True

    def __init__(self, server_name):
        # Create sample production.db in root folder
        db.flush_db(DB_FILE)
        db.create_book_table(DB_FILE)
        db.add_sample_books(DB_FILE)

        # Create bluetooth server and start it listening on a new thread
        self.server = server.BluetoothServer(server_name, self.parse_message)
        self.server_thread = Thread(target=self.server.start_server)
        self.server_thread.start()

        # Turn camera on and get it as object
        self.camera = vision.activate_camera()

        print('Waiting for bricks to be connected...')

        while not self.server.bricks_connected():
            time.sleep(1)

        # Move the robot at the beginning of first cell
        self.reset_position()
        # Initialize robot's vertical position to be the bottom row: (TODO: check if we can get rid of this assumption)
        self.current_shelf_level = 0
        self.aligned_to_book = None
        self.is_busy = False

        self.current_x_coordinate = 0

        # Assume both bricks are available (i.e. none of their motors is moving)
        self.BRICK_HORIZONTAL_MOVEMENT_state = self.BRICK_AVAILABLE_STATE
        self.BRICK_VERTICAL_MOVEMENT_state = self.BRICK_AVAILABLE_STATE

        # Stop all motors
        self.stop_motors()
        time.sleep(0.1)

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

    def get_cell_x_coordinate(self, cell):
        """
        |  4  |  5  |  6  |  7  |
        |-----------------------|
        |  0  |  1  |  2  |  3  |

        Get the index of that cell on its row and multiply by the width of a cell

        """
        cell %= self.CELLS_PER_ROW
        return cell * self.CELL_WIDTH

    def reset_position(self):
        self.server.send_to_device(self.server.make_message(status.MESSAGE_RESET_POSITION), BRICK_HORIZONTAL_MOVEMENT)

    def get_cell_shelf_level(self, cell):
        # 0 for bottom level, 1 for top level
        return int(cell / self.CELLS_PER_ROW)

    def reach_cell(self, cell):
        print('========================= enter reach_cell ===============================')
        print('---> Reaching cell: ' + str(cell))
        # TODO: Implement message from brick to RPI to be sent when vertical movement is finished
        # instead of waiting of hardcoded sleeping

        # Get the target x coordinate (the place where we want to move the robot)
        target_x_coordinate = self.get_cell_x_coordinate(cell)

        # Compute the offset with which the robot will be moved
        x_offset = self.current_x_coordinate - target_x_coordinate

        target_shelf_level = self.get_cell_shelf_level(cell)

        print('         --- To reach cell ' + str(cell) + ', we need to go to shelf level ' + str(target_shelf_level) +
              ' (now we are at level ' + str(self.current_shelf_level))

        if target_shelf_level == 0 and self.current_shelf_level == 1:
            # We are on the top row and want to reach some cell on the bottom row,
            # so first we do the vertical movement before the horizontal one
            self.server.send_to_device(self.server.make_message('down'), BRICK_VERTICAL_MOVEMENT)
            print("[reach_cell]: waiting for motor to free")
            time.sleep(8)
            self.current_shelf_level = 0

            self.server.send_to_device(self.server.make_message('horizontal', amount=x_offset),
                                       BRICK_HORIZONTAL_MOVEMENT)
        else:
            # We are on either bottom or top row but here we always make horizontal movement first
            self.server.send_to_device(self.server.make_message('horizontal', amount=x_offset),
                                       BRICK_HORIZONTAL_MOVEMENT)

            if self.current_shelf_level == 0 and target_shelf_level == 1:
                # Now we do the vertical movement if we were on level 0 but want to reach level 1
                self.server.send_to_device(self.server.make_message('up'), BRICK_VERTICAL_MOVEMENT)
                print("[reach_cell]: waiting for motor to free")
                time.sleep(8)
                self.current_shelf_level = 1

        # Update the current x_coordinate to be the target coordinate as the robot is now there
        self.current_x_coordinate = target_x_coordinate

        print('*************** finish reach_cell *********************')

    # TODO: Interface motor ready and stop message with brick
    def scan_ISBN(self, target_ISBN=None, full_scanning=False, cell=None):
        if target_ISBN is None:
            print('Scanning for any ISBN that might be at cell = ' + str(cell))
        else:
            print("Scanning for ISBN " + target_ISBN)

        # Give breathing time to the brick
        time.sleep(1)

        # Traverse the current cell and keep scanning while moving
        self.server.send_to_device(self.server.make_message('horizontal', amount=self.CELL_WIDTH),
                                   BRICK_HORIZONTAL_MOVEMENT)

        # Give time to the brick to process the message
        self.wait_until_brick_becomes(BRICK_HORIZONTAL_MOVEMENT, self.BRICK_BUSY_STATE)
        time.sleep(1)

        found_ISBN = None
        print('  Begin scanning for ISBN (left -> right)...current state of HORIZONTAL BRICK ' +
              str(self.BRICK_HORIZONTAL_MOVEMENT_state))
        while self.BRICK_HORIZONTAL_MOVEMENT_state == self.BRICK_BUSY_STATE:
            decoded_ISBN, offset = vision.read_QR(self.camera)
            if decoded_ISBN is not None:
                found_ISBN = decoded_ISBN

        # Now the state of the horizontal brick is 'available', it means horizontal movement has finished.
        # So we have to move the brick back to the beginning of the cell. Keep scanning just to
        # increase accuracy.

        # Give the brick some breathing time before returning it to the beginning of the cell
        time.sleep(1)

        print('  Continue scanning for ISBN...current state of HORIZONTAL BRICK ' +
              str(self.BRICK_HORIZONTAL_MOVEMENT_state))
        self.server.send_to_device(self.server.make_message('horizontal', amount=-self.CELL_WIDTH),
                                   BRICK_HORIZONTAL_MOVEMENT)

        # Give time to the brick to process the message
        self.wait_until_brick_becomes(BRICK_HORIZONTAL_MOVEMENT, self.BRICK_BUSY_STATE)

        while self.BRICK_HORIZONTAL_MOVEMENT_state == self.BRICK_BUSY_STATE:
            decoded_ISBN, offset = vision.read_QR(self.camera)
            if decoded_ISBN is not None:
                found_ISBN = decoded_ISBN

        print(' Finished scanning for ISBN...current state of HORIZONTAL BRICK is' +
              str(self.BRICK_HORIZONTAL_MOVEMENT_state))

        if full_scanning:
            if found_ISBN is not None:
                # noinspection PyBroadException
                try:
                    db.update_book_position(DB_FILE, str(found_ISBN), str(cell))
                except:
                    db.add_book(DB_FILE, str(found_ISBN), "", "", str(cell), db.STATUS_AVAILABLE)
                    print("Unknown book found, add ISBN to db")
            return

        if found_ISBN == target_ISBN:
            return True
        return False

    def send_message(self, socket, title, body=None):
        if body is not None:
            message = {title: body}
        else:
            message = {'message': {"content": title}}
            # message = {title: { } }
            print("sending message: " + json.dumps(message))
            socket.send(json.dumps(message))

    @primary_action
    @disruptive_action
    def find_book(self, socket, ISBN):
        """
        Move the robot at the position of the book having the title received
        as an argument.
        """

        print("The received ISBN is " + str(ISBN))
        cell = int(db.get_position_by_ISBN(DB_FILE, ISBN))
        print("The book, according to the information I have in the DB, should be at cell " + str(cell))

        if cell == -1:
            # TODO: discuss if this is good for the user
            # Position -1 means the book is not in the shelf (at least according to the robot's belief)
            socket.send(self.MESSAGE_MISSING_BOOK)
            return

        # Now we actually move to that cell
        self.reach_cell(cell)

        # TODO: current ignore wiggling and qr recognize on top shelf
        global IGNORE_QR_CODE
        if self.current_shelf_level == 1:
            IGNORE_QR_CODE = False
        else:
            IGNORE_QR_CODE = False
        IGNORE_QR_CODE = False
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
    def full_scan(self, socket=None, *args, **kwargs):
        all_ISBNs = db.get_all_ISBNs(DB_FILE)
        for item in all_ISBNs:
            ISBN = str(item[0])
            print('Current ISBN: ' + str(ISBN) + ' type = ' + str(type(ISBN)))
            # Assume the none of the books is in the shelf
            db.update_book_position(DB_FILE, ISBN, '-1')

        for current_cell in range(0, self.CELLS_PER_ROW):
            while self.BRICK_HORIZONTAL_MOVEMENT_state == self.BRICK_BUSY_STATE:
                time.sleep(0.1)
            self.reach_cell(current_cell)
            while self.BRICK_HORIZONTAL_MOVEMENT_state == self.BRICK_BUSY_STATE:
                time.sleep(0.1)
            self.scan_ISBN(full_scanning=True, cell=current_cell)

        # TODO: add state message for vertical brick

        for current_cell in range(2 * self.CELLS_PER_ROW, self.CELLS_PER_ROW, -1):
            while self.BRICK_HORIZONTAL_MOVEMENT_state == self.BRICK_BUSY_STATE:
                time.sleep(0.1)
            self.reach_cell(current_cell - 1)
            while self.BRICK_HORIZONTAL_MOVEMENT_state == self.BRICK_BUSY_STATE:
                time.sleep(0.1)
            self.scan_ISBN(full_scanning=True, cell=current_cell - 1)

        # Return to cell 0
        self.reach_cell(0)

    def stop_motors(self, ports=None):
        # TODO: do we need add sth about stopping a specific motor?
        # Currently, ignores the 'ports' argument for simplicity
        message = self.server.make_message('stop')
        self.server.send_to_device(message, Device.BRICK_33)
        self.server.send_to_device(message, Device.BRICK_13)

    def parse_message(self, data, socket):
        json_command = json.loads(data)

        command_type = list(json_command.keys())[0]
        command_args = json_command[command_type]

        # TODO: Add code onto receiving end (control.py I think, not ideal so do whatever feels right)
        if (command_type == 'move' and len(command_args) == 4 and 'ports' in command_args.keys()
                and 'speed' in command_args.keys() and 'brick' in command_args.keys()
                and 'time' in command_args.keys()):
            if command_args['brick'] == '13':
                # send to brick 13
                self.server.send_to_device(data, device_type=Device.BRICK_13)
                pass
            elif command_args['brick'] == '33':
                # send to brick 33
                self.server.send_to_device(data, device_type=Device.BRICK_33)
            else:
                raise ValueError('Invalid "brick" parameter: %s for "move" command!' % command_args['brick'])

            # self.rotate_motor(command_args['ports'], command_args['speed'], command_args['time'])

        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motors(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motors()
            else:
                raise ValueError('Invalid stop command')

        elif command_type == 'findBook' and len(command_args) == 1 and 'ISBN' in command_args.keys():
            self.find_book(socket, command_args['ISBN'])

        elif command_type == 'fullScan' and len(command_args) == 1 and 'ISBN' in command_args.keys():
            self.full_scan(socket, command_args['ISBN'])

        elif command_type == 'takeBook' and len(command_args) == 1:
            ISBN = command_args['ISBN']
            if self.aligned_to_book == ISBN:
                message = '{"takeBook":{}}'
                self.server.send_to_device(message, BRICK_BOOK_FETCHING)
                # Wait for book retrieval (time might need adjusted)
                time.sleep(15)
                # Set book to unavailable in database
                db.update_book_status(DB_FILE, ISBN, '0')
                self.reach_cell(0)
            else:
                socket.send(self.MESSAGE_BOOK_NOT_ALIGNED)

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
                message = {'bookList': built_query}
                socket.send(json.dumps(message))
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
        elif command_type == 'scan_over':
            self.scanning_over = True

        elif command_type == status.MESSAGE_AVAILABLE:
            if len(command_args) != 1:
                raise ValueError('Invalid arguments for MESSAGE_AVAILABLE')

            if command_args['brick_id'] == BRICK_HORIZONTAL_MOVEMENT:
                self.BRICK_HORIZONTAL_MOVEMENT_state = self.BRICK_AVAILABLE_STATE
            else:
                self.BRICK_VERTICAL_MOVEMENT_state = self.BRICK_AVAILABLE_STATE

        elif command_type == status.MESSAGE_BUSY:
            if len(command_args) != 1:
                raise ValueError('Invalid arguments for MESSAGE_BUSY')
            if command_args['brick_id'] == BRICK_HORIZONTAL_MOVEMENT:
                self.BRICK_HORIZONTAL_MOVEMENT_state = self.BRICK_BUSY_STATE
            else:
                self.BRICK_VERTICAL_MOVEMENT_state = self.BRICK_BUSY_STATE

        elif command_type == status.MESSAGE_LEFT_EDGE:
            print("Hit the left touch sensor")
            self.current_x_coordinate = 0

        elif command_type == status.MESSAGE_RIGHT_EDGE:
            print("Hit the right touch sensor")
            self.current_x_coordinate = self.ROBOT_RIGHT_COORDINATE

        elif command_type == status.MESSAGE_TOP_EDGE:
            self.current_shelf_level = 1
            print("Hit the TOP touch sensor")

        elif command_type == status.MESSAGE_BOTTOM_EDGE:
            self.current_shelf_level = 0
            print("Hit the BOTTOM touch sensor")

        else:
            print("unknown message")

    def send_busy_message(self, socket):
        socket.send(self.MESSAGE_BUSY)

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

    def wait_until_brick_becomes(self, brick_id, brick_state):
        if brick_id == BRICK_HORIZONTAL_MOVEMENT:
            while self.BRICK_HORIZONTAL_MOVEMENT_state != brick_state:
                time.sleep(0.1)
        elif brick_id == BRICK_VERTICAL_MOVEMENT:
            while self.BRICK_VERTICAL_MOVEMENT_state != brick_state:
                time.sleep(0.1)

if __name__ == '__main__':
    # Initialize robot, starts listening for commands
    robot = Robot('raspberry-pi')

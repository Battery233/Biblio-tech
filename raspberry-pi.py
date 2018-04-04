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

# move vertical brick to level
# **********WARNING*********
# must make sure TOUCH_SENSOR in brick33.py is working when set MOVE_TO_LEVEL_0 true
# rpi will send a message to enable TOUCH_SENSOR in vertical brick even TOUCH_SENSOR_ENABLED in brick33.py is false
# TODO: to be tested
MOVE_TO_LEVEL_0 = False

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

    BOOK_WIDTH = 60
    # (former) CELL_WIDTH = 210
    CELL_WIDTH = 115
    CELLS_PER_ROW = 3

    ROBOT_RIGHT_COORDINATE = 480

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
        db.create_logs_table(DB_FILE)

        db.add_sample_books(DB_FILE)

        # Create bluetooth server and start it listening on a new thread
        self.server = server.BluetoothServer(server_name, self.parse_message)
        self.server_thread = Thread(target=self.server.start_server)
        self.server_thread.start()

        # Turn camera on and get it as object
        self.camera = vision.activate_camera()

        print('Waiting for bricks to be connected...')

        self.scan_interval = 60  # minutes
        while not self.server.bricks_connected():
            time.sleep(1)

        # Stop all motors
        self.stop_motors()
        time.sleep(0.1)

        # Initialize robot's vertical position to be the bottom row: (TODO: check if we can get rid of this assumption)
        self.current_shelf_level = 0
        self.aligned_to_book = None
        self.is_busy = False

        self.current_x_coordinate = 0

        # move BRICK_VERTICAL to level 0: only use this when bottom touch sensor is working:
        if MOVE_TO_LEVEL_0:
            self.server.send_to_device(self.server.make_message('enable_vertical_touch_sensor'),
                                       BRICK_VERTICAL_MOVEMENT)
            self.server.send_to_device(self.server.make_message('down'), BRICK_VERTICAL_MOVEMENT)

        # Move the robot at the beginning of the shelf, i.e. at the retrieval position.
        self.reset_position()

        # start periodic scanning
        while True:
            time.sleep(self.scan_interval * 60)  # multiply by 60 to make'em actually minutes
            self.full_scan()

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
                |  3  |  4  |  5  |
                |------------------
        <------>|  0  |  1  |  2  |

        The beginning of the cell is hardcoded now (this includes the offset given by the retrieval space).

        """

        coordinates = [180, 320, 460]
        row_index = cell % self.CELLS_PER_ROW

        return coordinates[row_index]

    def reset_position(self):
        if self.current_shelf_level == 1:
            # We are on the top row and want to reach the 0 cell, on the bottom row,
            # so first we do the vertical movement before the horizontal one
            self.server.send_to_device(self.server.make_message('down'), BRICK_VERTICAL_MOVEMENT)
            print("[reach_cell]: waiting for motor to free")
            time.sleep(8)
            self.current_shelf_level = 0

        self.server.send_to_device(self.server.make_message(status.MESSAGE_RESET_POSITION), BRICK_HORIZONTAL_MOVEMENT)
        self.current_x_coordinate = 0

    def get_cell_shelf_level(self, cell):
        # 0 for bottom level, 1 for top level
        return int(cell / self.CELLS_PER_ROW)

    def reach_cell(self, cell):
        print('========================= enter reach_cell ===============================')
        print('---> Reaching cell: ' + str(cell))

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
            time.sleep(4)
        else:
            # We are on either bottom or top row but here we always make horizontal movement first
            self.server.send_to_device(self.server.make_message('horizontal', amount=x_offset),
                                       BRICK_HORIZONTAL_MOVEMENT)
            time.sleep(4)

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
        """

        :param target_ISBN: the ISBN we are looking for (or None if we just want to update the database)
        :param full_scanning: True if we are proceeding a full scanning and False if this we only scan the current cell
        :param cell: the cell we are scanning
        :return: True if the scan succeeded and the "target_ISBN" is found in the current cell. False if we found
                 a different ISBN or if we're not looking for a specific ISBN
        """
        if target_ISBN is None:
            print('Scanning for any ISBN that might be at cell = ' + str(cell))
        else:
            print("Scanning for ISBN " + target_ISBN)

        # Give breathing time to the brick
        time.sleep(0.5)

        # TODO: FIX AMOUNT
        self.server.send_to_device(self.server.make_message('horizontal_scan', amount=-self.CELL_WIDTH / 2),
                                   BRICK_HORIZONTAL_MOVEMENT)

        # Do a number of mock attempts to forget about the cached QR code
        for mock_attempt in range(0, 10):
            decoded_ISBN, offset = vision.read_QR(self.camera)
        decoded_ISBN = None

        found_ISBN = None
        print('  Begin scanning for ISBN (left -> right)...')
        for attempt in range(20):
            decoded_ISBN, offset = vision.read_QR(self.camera)
            if decoded_ISBN is not None:
                found_ISBN = decoded_ISBN
            print('Attempt #' + str(attempt) + '...decoded_ISBN: ' + str(decoded_ISBN))


        # Now the robot has (probably) reached the end of the cell.
        # So we have to move it back to the beginning of the cell. Keep scanning just to
        # increase accuracy.

        # Give the robot some breathing time to make sure it reaches the end of the cell
        # before returning it to the beginning of the cell
        time.sleep(5)

        print('  Continue scanning for ISBN...current state of HORIZONTAL BRICK ')

        # TODO: FIX AMOUNT
        self.server.send_to_device(self.server.make_message('horizontal_scan', amount=self.CELL_WIDTH / 2),
                                   BRICK_HORIZONTAL_MOVEMENT)

        print('  Begin scanning for ISBN (right -> left)...')
        for attempt in range(20):
            decoded_ISBN, offset = vision.read_QR(self.camera)
            if decoded_ISBN is not None:
                found_ISBN = decoded_ISBN
            print('Attempt #' + str(attempt) + '...decoded_ISBN: ' + str(decoded_ISBN))

        print(' Finished scanning for ISBN...; found ISBN ' + str(found_ISBN))

        # Give the robot some breathing time after it finished scanning
        print('Update book with ISBN ' + str(found_ISBN) + ' to now be at cell ' + str(cell))
        time.sleep(5)

        if found_ISBN is not None:
            self.aligned_to_book = found_ISBN

        if full_scanning:
            if found_ISBN is not None:
                # noinspection PyBroadException
                try:
                    db.update_book_position(DB_FILE, str(found_ISBN), str(cell))
                    print('Update book with ISBN ' + str(found_ISBN) + ' to now be at cell ' + str(cell))
                    db.update_book_status(DB_FILE, found_ISBN, '1')
                except:
                    print("Unknown book found!")

                title = db.get_title_by_ISBN(DB_FILE, found_ISBN)
                if title:
                    db.add_log(DB_FILE, str(cell), found_ISBN, title=title)
                else:
                    db.add_log(DB_FILE, str(cell), found_ISBN)


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
        available = int(db.get_book_status_by_ISBN(DB_FILE, ISBN))
        print("available = " + str(available))

        if not available:
            print("The book is not available, according to what I know")
            self.send_message(socket, self.MESSAGE_MISSING_BOOK)
            return

        print("The book, according to the information I have in the DB, should be at cell " + str(cell))

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
        if IGNORE_QR_CODE or self.scan_ISBN(ISBN, cell=cell):
            print("[FindBook] sending message: book found")
            self.send_message(socket, self.MESSAGE_FOUND_BOOK)
        else:
            self.send_message(socket, self.MESSAGE_MISSING_BOOK)

    @primary_action
    @disruptive_action
    def full_scan(self, socket=None, target_ISBN=None, *args, **kwargs):
        for current_cell in range(0, self.CELLS_PER_ROW):
            self.reach_cell(current_cell)

            if self.full_scan_cell(current_cell, socket=socket, target_ISBN=target_ISBN):
                self.send_message(socket, self.MESSAGE_FOUND_BOOK)
                return

        for current_cell in range(2 * self.CELLS_PER_ROW - 1, self.CELLS_PER_ROW - 1, -1):
            self.reach_cell(current_cell)

            if self.full_scan_cell(current_cell, socket=socket, target_ISBN=target_ISBN):
                self.send_message(socket, self.MESSAGE_FOUND_BOOK)
                return

        # Return to the retrieval position
        self.reset_position()

    # RETURNS TRUE IF IT HAS TO STOP SCANNING (FOUNDBOOK)
    def full_scan_cell(self, cell, socket=None, target_ISBN = None):
        if target_ISBN is not None:
            print('scanning cell looking for book')
            found = self.scan_ISBN(full_scanning=True, target_ISBN=target_ISBN, cell=cell)
            if found:
                print('In full scan, found book we were looking for')
                if socket is not None:
                    message = self.server.make_message(status.MESSAGE_FOUND_BOOK)
                    socket.send(message)
                return True

        else:
            print('scanning cell NOT looking for any book in particular')
            self.scan_ISBN(full_scanning=True, cell=cell)
            return False


    def stop_motors(self, ports=None):
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
                time.sleep(20)
                # Set book to unavailable in database (TODO: discuss about this and make sure it is consistent with
                # update_book_position)
                db.update_book_status(DB_FILE, ISBN, '0')
                self.reset_position()
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

        elif command_type == status.MESSAGE_GET_LOGS:
            query_result = db.get_logs(DB_FILE)
            built_query = []

            for i, book in enumerate(query_result):
                book_dict = {
                    'ISBN': query_result[i][0],
                    'title': query_result[i][1],
                    'pos': int(query_result[i][3]),
                }
                built_query.append(book_dict)

            print(built_query)
            message = {status.MESSAGE_LOGS: built_query}
            socket.send(json.dumps(message))

        elif command_type == status.MESSAGE_CLEAR_LOGS:
            db.clear_logs(DB_FILE)
            print('logs cleared in database')

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
        elif command_type == status.MESSAGE_GET_SCAN_INTERVAL:
            message = self.server.make_message(status.MESSAGE_SCAN_INTERVAL, interval=self.scan_interval)
            socket.send(message)
        elif command_type == status.MESSAGE_SET_SCAN_INTERVAL and len(command_args) == 1:
            self.scan_interval = int(command_args['interval'])
        else:
            print("unknown message received")

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


if __name__ == '__main__':
    # Initialize robot, starts listening for commands
    robot = Robot('raspberry-pi')

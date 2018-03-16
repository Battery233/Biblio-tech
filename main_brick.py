import json
import sys
import time
from threading import Thread

import ev3dev.ev3 as ev3

import control
import db.main as db
import vision.main as vision
from ev3bt import ev3_server

# FOR HARCODE:

IGNORE_QR_CODE = False

WEALTH_OF_NATIONS_ISBN = 9781840226881
THE_CASTLE_ISBN = 9780241197806

DB_FILE = db.PRODUCTION_DB


# just a test

def primary_action(action):
    """
    Method decorator to check whether robot is busy with some other operation
    before having it start a new action, and to prevent other actions from
    starting
    """

    def safety_wrapper(self, socket, *args, **kwargs):
        # If state is already busy trying to change it will return False
        if not self.state_wait():
            self.send_busy_message(socket)
            print('Robot was busy and was not able to perform action')
            print(self.state)
            return

        # If any of the motors is busy, robot is busy
        for motor in self.MOTORS:
            if motor.connected and not self.motor_ready(motor):
                self.send_busy_message(socket)
                print('Some motors were busy and robot was not able to perform action')
                return

        # Perform the action described by the method
        action(self, socket, *args, **kwargs)

        # Free the robot
        self.state_signal()

    return safety_wrapper


def disruptive_action(action):
    def break_get_book_flow(self, socket, *args, **kwargs):
        # Break the flow of findBook - takeBook. Sorry user, too slow
        self.state['alignedToBook'] = None

        action(self, socket, *args, **kwargs)

    return break_get_book_flow


def send_message(socket, title, body=None):
    # generate message and send json file
    if body is not None:
        message = {title: body}
    else:
        message = {'message': {"content": title}}

    print("sending message: " + json.dumps(message))
    socket.send(json.dumps(message))


class MainController(control.Controller):
    # TODO: change assumption that robot is initially positioned at the end of
    # the track
    INITIAL_STATE = {'alignedToBook': None, 'busy': False}

    # Socket A -> horizontal movement

    SOCKETS = [0, 3]
    MOTORS = [
        ev3.Motor('outA'),
        ev3.Motor('outB'),
        ev3.Motor('outC'),
        ev3.Motor('outD')
    ]

    TOUCH_SENSOR = ev3.TouchSensor()

    # finger: 55 dps per 1500 sec

    HORIZONTAL_SOCKET = 0
    HORIZONTAL_MOTOR = control.Controller.MOTORS[HORIZONTAL_SOCKET]

    HORIZONTAL_SPEED = 360
    HORIZONTAL_SPEED_FOR_SCANNING = int(HORIZONTAL_SPEED / 4)
    HORIZONTAL_MOVEMENT_FOR_SCANNING = 55

    # TODO: Finalise distance sensor offset
    DIST_BETWEEN_RIGHT_END_OF_RAILS_AND_GREEN_WALL = 70  # TODO: compute this again
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

        # Check motors
        for i, motor in enumerate(self.MOTORS):
            if not motor.connected:
                print('Motor ' + str(motor) + ' not connected')

        # Initialize robot's x_coordinate to 0:
        self.current_x_coordinate = 0

        # Initialize robot's vertical position to be the bottom row: (TODO: check if we can get rid of this assumption)
        self.bottom_row = True

        # Initialize robot's internal model
        self.state = self.INITIAL_STATE

        # Turn camera on and get it as object
        self.camera = vision.activate_camera()

        # Stop all motors
        self.stop_motors()

        self.dist_sensor = ev3.UltrasonicSensor()

        if not self.dist_sensor.connected:
            print("Distance sensor not connected")
        else:
            self.dist_sensor.mode = 'US-DIST-CM'

        if not self.TOUCH_SENSOR.connected:
            print("Unsafe! Touch sensor not connected")

        # Move the robot at the beginning of first cell
        self.reach_cell(0)

        super().__init__(server_name);

    def state_wait(self):
        if self.state['busy']:
            return False
        else:
            self.state['busy'] = True
            return True

    def state_signal(self):
        self.state['busy'] = False
        print('Ending action, freeing robot')

    def get_pos(self):
        """
        This is how this works:
        1. Take n (= 10) measurements of the distance and then average them to get a better estimate of the distance
           (don't forget to reset the mode of the sensor so that it takes a new measurement provided that the API documentation
            is right)
        2. Let dist_between_sensor_right_end_and_green_wall be the average from step 1
        3. Use maths to compute our x_coordinate (this is defined by the position of the very beginning of the white bar
           that supports the robot):
                       <- d ->
                       *******=oo<--------------- c ------------------>|           |
                        ****                                           | THE GREEN |
                         **                                            |   WALL    |
           ============x=====================================<--- b -->|           |
           <-------------------- a ------------------------->

           === LEGEND ===
           The object formed by stars (*) is the robot.
           The "=oo" thing is the sensor. c is the distance returned by the sensor's `value()` method (at least that's my
           understanding but we should definitely take more measurements and be sure that's correct)
           The "===================================" line are the rails and "THE GREEN WALL", well, it is the green wall.
           The 'x' within the "=====" line is the value that we are trying to compute.

           a = length of rails alone
           b = distance from the end of rails to the green wall
           c = distance from the end of sensor to the wall
           d = length of the robot

           Hence x is just a + b - (c + d) and then the robot will have to move -x (so that it moves backwards) in order
           to reach cell 0.

        It worked on most of the test, I think the success depends on how accurate the sensor gets the distance to the
        green wall. We MUST make a larger (both in width and height) target.
        """
        if not self.dist_sensor.connected:
            print('Distance sensor not connected')
            return None

        sum_of_distances = 0
        num_measurements = 10
        for i in range(0, num_measurements):
            time.sleep(0.25)
            self.dist_sensor.mode = 'US-DIST-CM'

            dist_now = self.dist_sensor.value()
            print("measurement #" + str(i) + ": " + str(dist_now))

            sum_of_distances += dist_now

        dist_between_sensor_right_end_and_green_wall = int(sum_of_distances / num_measurements)
        x_coordinate = self.RAILS_LENGTH + self.DIST_BETWEEN_RIGHT_END_OF_RAILS_AND_GREEN_WALL \
                       - (dist_between_sensor_right_end_and_green_wall + self.ROBOT_LENGTH)

        print("The distance between the right end of the sensor and the green wall is: " + str(
            dist_between_sensor_right_end_and_green_wall))
        print("My guess for the x_coordinate is: " + str(x_coordinate))

        return x_coordinate

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
            message = '{"up":{}}'
            self.server.send_to_device(message, ev3_server.Device.OTHER_EV3)
            time.sleep(8)
            self.bottom_row = False
        elif cell <= 1 and not self.bottom_row:
            message = '{"down":{}}'
            self.server.send_to_device(message, ev3_server.Device.OTHER_EV3)
            time.sleep(8)
            self.bottom_row = True

        print("Move the robot by " + str(x_offset))
        self.move_motor_by_dist(self.HORIZONTAL_MOTOR, x_offset, self.HORIZONTAL_SPEED)

        # Update the current x_coordinate to be the target coordinate as the robot is now there
        self.current_x_coordinate = target_x_coordinate

        print("[reach_cell]: waiting for motor to free")
        self.wait_for_motor(self.HORIZONTAL_MOTOR)
        print("[reach_cell]: action complete")

    def scan_ISBN(self, ISBN):
        print("Scanning for ISBN " + ISBN)

        decoded_ISBN = 0

        # The mock attempts are needed because I (Mihai) believe that somehow the previous QR code is cached and
        # the new one is not retrieved. TODO: check if this is really needed but there's definetly no harm in
        # keeping it other than it makes the whole process a little bit longer.
        num_mock_attempts = 3
        for attempt in range(0, num_mock_attempts):
            time.sleep(0.1)
            decoded_ISBN, offset = vision.read_QR(self.camera)

        # Now real scanning begins.
        num_attempts = 50
        found = False

        # This variable will flip from negative to positive as long as the scanning continues. First time it is
        # positive, which means the robot will start moving to the left.
        movement = self.HORIZONTAL_MOVEMENT_FOR_SCANNING
        for attempt in range(0, num_attempts):
            time.sleep(0.1)
            decoded_ISBN, offset = vision.read_QR(self.camera)

            print("Attempt #" + str(attempt))
            print("The decoded ISBN is " + str(decoded_ISBN))
            if decoded_ISBN is not None:
                if int(ISBN) == int(decoded_ISBN):
                    print("=========== SUCCESS!")
                    found = True
                    break
                else:
                    print("Uuuups! Different ISBN found, so the book is not in the right place!")
                    break
            else:
                print("Still trying to detect the ISBN...")

            if self.motor_ready(self.HORIZONTAL_MOTOR):
                if movement > 0:
                    print("Wiggle to right... :) ---> ")
                else:
                    print("<--- Wiggle to left.... :)")
                    # The wiggle sound is actually not needed, but to discuss whether we can add sounds to inform
                    # the user about book title / finding of a book etc.
                    # ev3.Sound.speak("wiggle, wiggle, wiggle!")
                self.move_motor_by_dist(self.HORIZONTAL_MOTOR, movement, self.HORIZONTAL_SPEED_FOR_SCANNING)
                movement = -movement

        # If the value of "movement" is negative, it means that last time we moved to the left and because we finished
        # the loop (either because we found the book, or the number of attempts was exhausted), we have to return
        # the robot in the original position from which it started to wiggle.
        if movement < 0:
            # Firstly, wait for the motor to finish if it is still doing the previous movement.
            self.wait_for_motor(self.HORIZONTAL_MOTOR)
            self.move_motor_by_dist(self.HORIZONTAL_MOTOR, movement, self.HORIZONTAL_SPEED_FOR_SCANNING)

        if not found:
            print("Number of attempts exhausted... return False :( book is definitely not here")
        return found

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
            self.state['alignedToBook'] = ISBN
            print("[FindBook] sending message: book found")
            send_message(socket, self.MESSAGE_FOUND_BOOK)
        else:
            send_message(socket, self.MESSAGE_MISSING_BOOK)

    @primary_action
    @disruptive_action
    def full_scan(self, socket, ISBN):
        # TODO: A LOT
        pass

    # Moves motor by specified distance at a certain speed and direction
    # @param int    socket     Socket index in MOTORS to use
    # @param float  dist       Distance to move motor in centimeters
    # @param int    speed      Speed to move motor at (degrees / sec)
    def move_motor_by_dist(self, motor, dist, speed):
        if motor.connected:
            # convert to cm and then to deg
            angle = int(self.cm_to_deg(float(dist) / 10))
            motor.run_to_rel_pos(position_sp=angle, speed_sp=speed, )

            while not self.motor_ready(motor):
                if self.TOUCH_SENSOR.connected and self.TOUCH_SENSOR.is_pressed:
                    self.stop_motors([self.HORIZONTAL_SOCKET])
                time.sleep(0.1)
            print('motor stop ' + str(motor) + 'current location' + str(self.current_x_coordinate))
        else:
            print('[ERROR] No motor connected to ' + str(motor))

    def stop_motors(self, sockets=None):
        # Stop all the motors by default
        if sockets is None:
            sockets = self.SOCKETS
        for socket in sockets:
            m = self.MOTORS[socket]
            if m.connected:
                m.stop(stop_action='brake')

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
            if self.state['alignedToBook'] == ISBN:
                message = '{"takeBook":{}}'
                self.server.send_to_device(message, ev3_server.Device.OTHER_EV3)
                time.sleep(23)
                self.reach_cell(0)
            else:
                send_message(socket, self.MESSAGE_BOOK_NOT_ALIGNED)

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
            if len(command_args) == 1 and 'title' in command_args.keys():
                query_result = self.query_DB(command_args['title'])
                if query_result is not None:
                    args = (command_args['title'], query_result)
                else:
                    args = None
                send_message(socket, 'bookItem', args)
            elif len(command_args) == 0:
                print("[DBS in control.py]Give the book list of all books.")
                query_result = self.query_DB()
                built_query = []

                for i, book in enumerate(query_result):
                    book_dict = {'ISBN': query_result[i][0], 'title': query_result[i][1], 'author': query_result[i][2],
                                 'pos': int(query_result[i][3]), 'avail': query_result[i][4]}
                    built_query.append(book_dict)

                print(built_query)
                send_message(socket, 'bookList', built_query)
            else:
                raise ValueError('Invalid arguments for queryDB')

        elif command_type == 'close':
            self.server.close_server()
            self.server_thread.join()
            sys.exit(0)

        elif command_type == 'ping':
            socket.send('pong')

        elif command_type == 'vertical_success':
            pass

        elif command_type == 'vertical_failure':
            print("Error happened when trying to move vertically")

    def send_busy_message(self, socket):
        send_message(socket, self.MESSAGE_BUSY)

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
    robot = MainController('ev3_main')

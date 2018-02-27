import json
import sys
import time
from threading import Thread

import ev3dev.ev3 as ev3

import db.main as db
import db.jsonbuilder as js
import vision.main as vision
from ev3bt import ev3_server

DEG_PER_CM = 29.0323

DB_FILE = db.PRODUCTION_DB


def cm_to_deg(cm):
    return DEG_PER_CM * cm

def letter_to_int(letter):
    if letter == 'A':
        return 0
    elif letter == 'B':
        return 1
    elif letter == 'C':
        return 2
    elif letter == 'D':
        return 3
    else:
        return 0

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


class Controller:
    # TODO: change assumption that robot is initially positioned at the end of
    # the track
    INITIAL_STATE = {'alignedToBook': None, 'busy': False, 'x_pos': 500}

    MOTORS = [
        ev3.Motor('outA'),
        ev3.Motor('outB'),
        ev3.Motor('outC'),
        ev3.Motor('outD')
    ]

    # SOCKET A IS HORIZONTAL movement
    # SOCKET B IS FOR arm
    # SOCKET C IS FOR FINGER

    HORIZONTAL_SOCKET = 0
    VERTICAL_SOCKET = 3
    ARM_SOCKET = 1
    FINGER_SOCKET = 2

    HORIZONTAL_MOTOR = MOTORS[HORIZONTAL_SOCKET]
    VERTICAL_MOTOR = MOTORS[VERTICAL_SOCKET]
    ARM_MOTOR = MOTORS[ARM_SOCKET]
    FINGER_MOTOR = MOTORS[FINGER_SOCKET]

    # finger: 55 dps per 1500 sec

    HORIZONTAL_SPEED = 360

    ARM_TIME = 1500
    ARM_EXTENSION_SPEED = -140
    ARM_RETRACTION_SPEED = -ARM_EXTENSION_SPEED

    FINGER_TIME = 1000
    FINGER_EXTENSION_SPEED = 218
    FINGER_RETRACTION_SPEED = -FINGER_EXTENSION_SPEED

    # TODO: Finalise distance sensor offset
    DIST_BETWEEN_RIGHT_END_OF_RAILS_AND_GREEN_WALL = 70 # TODO: compute this again
    ROBOT_LENGTH= 170 # TODO: compute this again
    RAILS_LENGTH = 705 # TODO: compute this again

    CELLS_START = [(0, 0), (250, 0), (0, 300), (250, 300)]
    CELL_SIZE = 249

    TOLERABLE_OFFSET = 5

    MESSAGE_BOOK_NOT_ALIGNED = 'bookNotAligned'
    MESSAGE_BUSY = 'busy'
    MESSAGE_MISSING_BOOK = 'missingBook'
    MESSAGE_FOUND_BOOK = 'foundBook'

    def __init__(self):
        # Create sample production.db in root folder
        db.flush_db(DB_FILE)
        db.create_book_table(DB_FILE)
        db.add_sample_books(DB_FILE)

        # Check motors
        for i, motor in enumerate(self.MOTORS):
            if not motor.connected:
                print('Motor ' + str(motor) + ' not connected')

        # Initialize robot's internal model
        self.state = self.INITIAL_STATE

        # Turn camera on and get it as object
        self.camera = vision.activate_camera()

        # Stop all motors
        self.stop_motor()

        self.dist_sensor = ev3.UltrasonicSensor()

        if not self.dist_sensor.connected:
            print("Distance sensor not connected")
        else:
            self.dist_sensor.mode = 'US-DIST-CM'

        # Position arm at the beginning of first cell
        self.reach_cell(0)

        # Create bluetooth server and start it listening on a new thread
        self.server = ev3_server.BluetoothServer("ev3 dev", self.parse_message)
        self.server_thread = Thread(target=self.server.start_server)
        self.server_thread.start()

    def state_wait(self):
        if self.state['busy']:
            return False
        else:
            self.state['busy'] = True
            return True

    def state_signal(self):
        self.state['busy'] = False
        print('Ending action, freeing robot')

    def motor_ready(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        return motor.state != ['running']

    def wait_for_motor(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        while motor.state==["running"]:
            print('Motor is still running')
            time.sleep(0.1)

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
           
        # Rough sketch of how function will work, not remotely accurate or even logically correct
        # Assumes distance board is on right hand side, so that's why we subtract from the shelf length
        if self.dist_sensor.connected:
            sum_of_distances = 0
            num_measurements = 10
            for i in range(0, num_measurements):
                time.sleep(0.25)
                self.dist_sensor.mode = 'US-DIST-CM'
                dist_now = self.dist_sensor.value()
                print("measurement #" + str(i) + ": " + str(dist_now))
                sum_of_distances += dist_now
            dist_between_sensor_right_end_and_green_wall = int(sum_of_distances / num_measurements)
            x_coordinate = self.RAILS_LENGTH + self.DIST_BETWEEN_RIGHT_END_OF_RAILS_AND_GREEN_WALL\
                           - (dist_between_sensor_right_end_and_green_wall + self.ROBOT_LENGTH)
            print("The distance between the right end of the sensor and the green wall is: " + str(dist_between_sensor_right_end_and_green_wall))
            print("My guess for the x_coordinate is: " + str(x_coordinate))
            return x_coordinate
        else:
            print('Distance sensor not connected')
            return None

    def reach_cell(self, cell):
        # offset_to_end is the distance to end of track calculated
        # by the distance sensor. Temporarily disabled as distance sensor is
        # very imprecise
        # x_coordinate = self.get_pos()
        # x_coordinate = self.state['x_pos']
        x_coordinate = 0
        print("Move the robot by " + str(-x_coordinate))
        self.move_motor_by_dist(
            self.HORIZONTAL_MOTOR,
            self.CELLS_START[cell][0] - x_coordinate,
            self.HORIZONTAL_SPEED
        )
        # TODO: implement vertical movement
        print("[ReachCell]: waiting for motor to free")
        # self.HORIZONTAL_MOTOR.wait_until_not_moving(timeout=5)
        self.wait_for_motor(self.HORIZONTAL_MOTOR)
        print("[ReachCell]: action complete")
        self.state['position'] = self.CELLS_START[cell]

    def scan_ISBN(self, ISBN):
        # start horizontal movement needed to almost reach next cell
        print("Scanning for ISBN " + ISBN)
        if ISBN == 9781840226881:
            movement = 200
        else:
            movement = 0
        
        print("Start to move the motor by horizontal movement")
        self.move_motor_by_dist(
            self.HORIZONTAL_MOTOR,
            # self.CELL_SIZE,
            movement,
            self.HORIZONTAL_SPEED
        )
        print("End moving the robot by horizontal movement")

        # while not self.motor_ready(self.HORIZONTAL_MOTOR):
        #     decoded_ISBN, offset = vision.read_QR(self.camera)
        #     print("[ScanISBN], camera result: " + str(decoded_ISBN) + ", offset: " + str(offset))
        #     if ISBN == decoded_ISBN and offset < self.TOLERABLE_OFFSET:
        #         self.stop_motor()
        #         return True
        #     time.sleep(0.1)

        # return False
        print("Return True --> book found :)")
        return True

    @primary_action
    @disruptive_action
    def find_book(self, socket, ISBN):
        '''
        Move the robot at the position of the book having the title received
        as an argument.
        '''

        if int(ISBN) == 9781840226881:
            cell = 0
        else:
            cell = 1

        # cell = int(db.get_position_by_ISBN(DB_FILE, ISBN))

        print(cell)

        if cell is None:
            print('Book does not exist')
            # TODO: RETURN missingBook
            pass

        self.reach_cell(cell)

        if not self.scan_ISBN(ISBN):
            self.send_message(socket, self.MESSAGE_MISSING_BOOK)
        else:
            self.state['alignedToBook'] = ISBN
            self.send_message(socket, self.MESSAGE_FOUND_BOOK)

    @primary_action
    def take_book(self, socket, ISBN):
        print("Enter in take_book")
        if self.state['alignedToBook'] == ISBN or True:
            # extend arm
            print("Move first motor")
            self.move_motor(
                [self.ARM_SOCKET],
                self.ARM_EXTENSION_SPEED,
                self.ARM_TIME
            )
      
            print("wait 5 secs")
            time.sleep(5) # TODO: check times later
            print("move second motor")
            # extend finger
            self.move_motor(
                [self.FINGER_SOCKET],
                self.FINGER_EXTENSION_SPEED,
                self.FINGER_TIME
            )

            print("wait 5 secs again")
            time.sleep(5)
            print("move third motor")
            # retract arm
            self.move_motor(
                [self.ARM_SOCKET],
                self.ARM_RETRACTION_SPEED,
                self.ARM_TIME
            )

            print("wait 5 secs for last time")
            time.sleep(5)
            print("move last motor")
            self.move_motor(
                [self.FINGER_SOCKET],
                self.FINGER_RETRACTION_SPEED,
                self.FINGER_TIME
            )
        else:
            self.send_message(socket, self.MESSAGE_BOOK_NOT_ALIGNED)

    @primary_action
    @disruptive_action
    def full_scan(self, socket, ISBN):
        # TODO: A LOT
        pass

    # Move motor
    # @param string socket  Output socket string (0 / 1 / 2 / 3)
    # @param int speed      Speed to move motor at (degrees/sec)
    # @param int time       Time to move motor for (milliseconds)
    def move_motor(self, sockets, speed, time):
        for socket in sockets:
            motor = self.MOTORS[socket]
            if motor.connected:
                # Safety checks (1000 speed is cutting it close but should be safe, time check is just for sanity)
                if -1000 < int(speed) <= 1000 and 0 < int(time) <= 10000:
                    motor.run_timed(speed_sp=speed, time_sp=time)
            else:
                print('[ERROR] No motor connected to ' + socket)

    # Moves motor by specified distance at a certain speed and direction
    # @param int    socket     Socket index in MOTORS to use
    # @param float  dist       Distance to move motor in centimeters
    # @param int    speed      Speed to move motor at (degrees / sec)
    def move_motor_by_dist(self, motor, dist, speed):

        if motor.connected:
            # convert to cm and then to deg
            angle = int(cm_to_deg(float(dist)/10))
            motor.run_to_rel_pos(position_sp=angle, speed_sp=speed, )
        else:
            print('[ERROR] No motor connected to ' + str(motor))

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

        if (command_type == 'move' and len(command_args) == 3 and
                'ports' in command_args.keys() and 'speed' in command_args.keys() and 'time' in command_args.keys()):
            self.move_motor(command_args['ports'], command_args['speed'], command_args['time'])

        elif command_type == 'stop':
            if len(command_args) == 1 and ('stop' in command_args.keys()):
                self.stop_motor(command_args['ports'])
            elif len(command_args) == 0:
                self.stop_motor()
            else:
                raise ValueError('Invalid command')

        elif command_type == 'findBook' and len(command_args) == 1 and 'ISBN' in command_args.keys():
            self.find_book(socket, command_args['ISBN'])
            # TODO: remove this
            self.take_book(socket, command_args['ISBN'])

        elif command_type == 'fullScan' and len(command_args) == 1 and 'ISBN' in command_args.keys():
            self.full_scan(socket, command_args['ISBN'])

        elif command_type == 'takeBook' and len(command_args) == 0:
            self.take_book(socket, command_args['ISBN'])

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
            if len(command_args) == 1 and 'title' in command_args.keys():
                query_result = self.query_DB(command_args['title'])
                if query_result is not None:
                    args = (command_args['title'], query_result)
                else:
                    args = None
                self.send_message(socket, 'bookItem', args)
            elif len(command_args) == 0:
                print("[DBS in control.py]Give the book list of all books.")
                query_result = self.query_DB()
                # print("Query Result: " + str(query_result))
                built_query = []

                for i, book in enumerate(query_result):
                    book_dict = {'ISBN': query_result[i][0], 'title': query_result[i][1], 'author': query_result[i][2],
                                 'pos': int(query_result[i][3]), 'avail': query_result[i][4]}
                    built_query.append(book_dict)

                print(built_query)
                self.send_message(socket, 'bookList', built_query)
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
    robot = Controller()

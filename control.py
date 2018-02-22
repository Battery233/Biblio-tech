import db.main as db
import ev3dev.ev3 as ev3

import time

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

    def __init__(self, camera, state=INITIAL_STATE):
        self.state = state
        self.camera = camera

    def reachCell(self, cell):
        # do some movement
        waitForMotor(motor)
        self.state['position'] = CELLS[cell]

    def scanISBN(self, ISBN):
        # start horizontal movement needed to almost reach next cell

        while(not motorReady(motor)):
            decoded_ISBN, offset = vision.read_QR(self.camera)
            if ISBN == decoded_ISBN and offset < TOLERABLE_OFFSET:
                # stop motor
                return True
            time.sleep(0.1)

        return False


    def findBook(self, title):
		'''
		Move the robot at the position of the book having the title received
		as an argument.
		'''
        cell = db.get_position_by_title(title)
		if cell is None:
			print('Book does not exist')
			return

        reachCell(cell)
		ISBN = db.get_ISBN_by_title(title)
        if not scanISBN(ISBN):
            fullScan(ISBN)
        else:
            self.state['alignedToBook'] = ISBN
            return state


    def takeBook(self):
        pass

    def fullScan(self, ISBN):
        pass

    def waitForMotor(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        while motor.state==["running"]:
            print('Motor is still running')
            time.sleep(0.1)

    def motorReady(self, motor):
        # Make sure that motor has time to start
        time.sleep(0.1)
        return motor.state != ['running']

    # Move motor
    # @param string socket  Output socket string (0 / 1 / 2 / 3)
    # @param int speed      Speed to move motor at (degrees/sec)
    # @param int time       Time to move motor for (milliseconds)
    def move_motor(self, socket, speed, time):
        motor = MOTORS[socket]
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
            m = MOTORS[socket]
            if m.connected:
                m.stop(stop_action='brake')

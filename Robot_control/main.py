import db.main as db
import vision.main as vision
import Robot_control.utils as utils

import ev3dev.ev3 as ev3

import time

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

motors = [
    ev3.LargeMotor('outA'),
    ev3.LargeMotor('outB'),
    ev3.LargeMotor('outC'),
    ev3.LargeMotor('outD')
    ]

CELLS_START = [(0,0), (500,0), (0,500), (500,500)]
TOLERABLE_OFFSET = 5

# temporary assumption: shelf goes from 0 to 1000 in mm
state = {'alignedToBook': None}
canera = None

def startUp():
    reachCell(0)
    camera = vision.activate_camera()

    for motor in motors:
        motor.connected

def reachCell(cell):
    # do some movement
    waitForMotor(motor)
    state['position'] = CELLS[cell]

def scanISBN(ISBN):
    # start horizontal movement needed to almost reach next cell

    while(not motorReady(motor)):
        decoded_ISBN, offset = vision.read_QR(camera)
        if ISBN == decoded_ISBN and offset < TOLERABLE_OFFSET:
            # stop motor
            return True
        time.sleep(0.1)

    return False


def reachBook(ISBN):
    cell = db.get_position_by_ISBN(ISBN)
    reachCell(cell)
    if not scanISBN(ISBN):
        completeScan(ISBN)
    else:
        state['alignedToBook'] = ISBN

def takeBook():
    pass

def completeScan(ISBN):
    pass

def stop(port=None):
    pass

def queryDB(ISBN=None):
    pass


def waitForMotor(motor):
    # Make sure that motor has time to start
    time.sleep(0.1)
    while motor.state==["running"]:
        print('Motor is still running')
        time.sleep(0.1)

def motorReady(motor):
    # Make sure that motor has time to start
    time.sleep(0.1)
    return motor.state != ['running']

# IMPORTANT: TO BE RUN FROM THE MAIN BRICK

import control
import time
from ev3bt import ev3_server


if __name__ == '__main__':
    # Initialize robot, starts listening for commands
    robot = control.Controller('ev3_main')
    time.sleep(5)
    robot.server.send_to_device("up", ev3_server.Device.OTHER_EV3)

import ev3dev.ev3 as ev3
import main as vision
import time

SPEED = 100
TOLERABLE_OFFSET = 1000
DISPLACEMENT = 300

camera = vision.activate_camera()


DEG_PER_CM = 29.0323
def cm_to_deg(cm):
    return DEG_PER_CM * cm

def motor_ready(motor):
    # Make sure that motor has time to start
    time.sleep(0.1)
    return motor.state != ['running']

def stop_motor():
    m = ev3.Motor('outA')
    if m.connected:
        m.stop(stop_action='brake')

def move_motor_by_dist(motor, dist, speed):
    if motor.connected:
        # convert to cm and then to deg
        angle = int(cm_to_deg(float(dist)/10))
        motor.run_to_rel_pos(position_sp=angle, speed_sp=speed, )
    else:
        print('[ERROR] No motor connected to ' + str(motor))

move_motor_by_dist(
            ev3.Motor('outA'),
            DISPLACEMENT,
            SPEED
        )

while not motor_ready(ev3.Motor('outA')):
            decoded_ISBN, offset = vision.read_QR(camera)
            print(str(decoded_ISBN))
            if decoded_ISBN is not None and offset < TOLERABLE_OFFSET:
                stop_motor()
                print("HURRAY")
            else:
                print("CRAP")

import ev3dev.ev3 as ev3
import time

dist_sensor = ev3.UltrasonicSensor()

if not dist_sensor.connected:
    print("Distance sensor not connected")
else:
    dist_sensor.mode = 'US-DIST-CM'

    while(True):
        time.sleep(1)
        print(dist_sensor.value())
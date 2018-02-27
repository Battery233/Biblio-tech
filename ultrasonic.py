import ev3dev.ev3 as ev3
import time

dist_sensor = ev3.UltrasonicSensor()

if not dist_sensor.connected:
    print("Distance sensor not connected")
else:
    dist_sensor.mode = 'US-DIST-CM'

    while(True):
        # time.sleep(1)
        if dist_sensor.connected:
            sum_of_distances = 0
            num_measurements = 10
            for i in range(0, num_measurements):
                time.sleep(0.25)
                dist_sensor.mode = 'US-DIST-CM'
                dist_now = dist_sensor.value()
                print("measurement #" + str(i) + ": " + str(dist_now))
                sum_of_distances += dist_now
            dist_between_sensor_right_end_and_green_wall = int(sum_of_distances / num_measurements)
            print("The distance between the right end of the sensor and the green wall is: " + str(dist_between_sensor_right_end_and_green_wall))
        else:
            print('Distance sensor not connected')

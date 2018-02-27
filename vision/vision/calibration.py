import main
import pygame
import time

camera = main.activate_camera(source='/dev/video0')

for i in reversed(range(1,5)):
    print('waiting ' + str(i))
    time.sleep(1)

print('smile')
while True:
    ISBN, offset = main.read_QR(camera)

    if ISBN == None:
        print('No QR code detected')
    else:
        print("ISBN: %s, offset(mm): %s" % (ISBN, offset))



    # # Take input from camera
    # img = camera.get_image()
    # # Save camera input to file
    # pygame.image.save(img, main.CAMERA_VIEW_FILE)

    # symbol = main.get_QR_symbol(main.CAMERA_VIEW_FILE)
    #
    # if symbol is not None:
    #     c1, _, _, c2 = [item for item in symbol.location]
    #
    #     size = abs(c1[0] - c2[0])
    #
    #     print('detected qr code\'s size is ' + str(size))
    # else:
    #     print('no qr code detected')

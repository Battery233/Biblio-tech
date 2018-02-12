import main
import pygame
import time

camera = main.activate_camera()

for i in reversed(range(1,5)):
    print('waiting ' + str(i))
    time.sleep(1)

print('smile')
# Take input from camera
img = camera.get_image()
# Save camera input to file
pygame.image.save(img, main.CAMERA_VIEW_FILE)

symbol = main.get_QR_symbol(main.CAMERA_VIEW_FILE)

if symbol is not None:
    c1, _, _, c2 = [item for item in symbol.location]
    size = abs(c1 - c2)

    print('detected qr code\'s size is ' + str(size))
else:
    print('no qr code detected')

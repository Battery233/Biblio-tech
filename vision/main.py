import qrtools.qrtools
import pygame.camera
import time

CAMERA_VIEW_FILE = "camera_view.jpg"

def activate_camera():
    pygame.camera.init()
    camera = pygame.camera.Camera("/dev/video0",(640,480))
    camera.start()

    return camera

def read_QR(camera):
    # Take input from camera
    img = camera.get_image()
    # Save camera input to file
    pygame.image.save(img, CAMERA_VIEW_FILE)

    return decode_QR(CAMERA_VIEW_FILE)



def decode_QR(filename):
    qr = qrtools.QR()
    qr.decode(filename)
    return qr.data

if __name__ == '__main__':
    camera = activate_camera()
    for i in range(5):
        print(read_QR(camera))
        time.sleep(5)

    camera.stop()

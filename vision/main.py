import qrtools.qrtools
import pygame.camera

CAMERA_VIEW_FILE = "camera_view.jpg"

def get_camera_view(filename):
    pygame.camera.init()
    cam = pygame.camera.Camera("/dev/video0",(640,480))
    cam.start()
    img = cam.get_image()
    cam.stop()

    # Save camera input to file
    pygame.image.save(img, filename)


def decode_QR(filename):
    qr = qrtools.QR()
    qr.decode(filename)
    return qr.data

if __name__ == '__main__':
    get_camera_view(CAMERA_VIEW_FILE)
    print(decode_QR(CAMERA_VIEW_FILE))

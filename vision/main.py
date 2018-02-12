import zbar
import Image
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
    # create a reader
    scanner = zbar.ImageScanner()
    # configure the reader
    scanner.parse_config('enable')

    # obtain image data
    pil = Image.open(filename).convert('L')
    width, height = pil.size
    raw = pil.tobytes()
    # wrap image data
    image = zbar.Image(width, height, 'Y800', raw)

    # scan the image for barcodes
    result = scanner.scan(image)
    if result == 0:
        return (None, None)

    for symbol in image:
        pass

    # clean up
    del(image)

    # decode text in QR code
    data = symbol.data.decode(u'utf-8')

    # find corners
    a, b, c, d = [item for item in symbol.location]
    # compute center of mass: sum coordinates and divide by 4
    com = reduce(sum_tuples, [a,b,c,d], (0,0))
    com = tuple(map(lambda x: int(x/4), com))

    return (data, com)

def sum_tuples(t1, t2):
    a, b = t1
    c, d = t2
    return (a+c, b+d)

if __name__ == '__main__':
    camera = activate_camera()
    for i in range(5):
        print(read_QR(camera))
        time.sleep(5)

    camera.stop()

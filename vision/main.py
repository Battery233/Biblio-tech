try:
    from PIL import Image
except:
    import Image
import zbar
import pygame.camera
import time

CAMERA_VIEW_FILE = "camera_view.jpg"
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_X_CENTER = CAMERA_WIDTH / 2

ACTUAL_QR_SIDE = 300

def activate_camera(source='/dev/video0'):
    pygame.camera.init()
    camera = pygame.camera.Camera(source, (CAMERA_WIDTH,CAMERA_HEIGHT))
    camera.start()

    return camera

def read_QR(camera):
    # Take input from camera
    img = camera.get_image()
    # Save camera input to file
    pygame.image.save(img, CAMERA_VIEW_FILE)

    return decode_QR(CAMERA_VIEW_FILE)

def get_QR_symbol(filename):
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
        return None

    for symbol in image:
        pass

    # clean up
    del(image)

    return symbol

def decode_QR(filename):
    symbol = get_QR_symbol(filename)

    if symbol is None:
        return (None, None)

    # decode text in QR code
    data = symbol.data.decode(u'utf-8')

    # find corners
    a, b, c, d = [item for item in symbol.location]

    # compute center of mass: sum coordinates element-wise and divide by 4
    com = reduce(sum_tuples, [a,b,c,d], (0,0))
    com = tuple(map(lambda x: int(x/4), com))

    # find horizontal offset in pixels (center of QR - center of camera)
    offset = com[0] - CAMERA_X_CENTER

    # find conversion to mm (ASSUMPTION: camera plane and QR parallel)
    img_top_side = abs(a[0] - d[0])
    pix_mm_rate = float(ACTUAL_QR_SIDE) / img_top_side

    # convert to mm
    offset = int(offset * pix_mm_rate)

    return (data, offset)

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

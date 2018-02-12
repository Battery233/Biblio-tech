# README
This is the vision component for Bibliotech

## Dependencies
Some dependencies need to be installed

```
sudo apt-get install libzbar-dev
sudo apt-get install python-zbar

sudo pip install pygame
sudo pip install Pillow
```

## How it works
Example usage:
```python
import vision.main as vision
import time

camera = vision.activate_camera()
# com is a tuple with the x and y coordinates of the center of mass of the QR code
ISBN, com = vision.read_QR(camera)

time.sleep(5)

next_ISBN, next_com = vision.read_QR(camera)

camera.stop()
```

If no QR code is detected, `read_QR(camera)` will return `(None, None)`.
*Note:* the EV3 brick will need some time to activate the camera, so that needs
to be done in the initial setup stage.

Running `main.py` will take an image from the camera and print the decoded QR
code text. This will happen 5 times at intervals of 5 seconds.

Running `vision/test.py` from the root folder of the project will run the tests

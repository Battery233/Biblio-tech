# README
This is the vision component for Bibliotech

## Dependencies
Some dependencies need to be installed

```
sudo apt-get install libzbar-dev
sudo apt-get install python-zbar

sudo pip install pygame
sudo pip install qrtools
sudo pip install Pillow
```

## How it works
Running `main.py` will take a snapshot of the current camera view and print to
the screen 'NULL' if it can't read a QR code or the text corresponding to the QR
code in the view.

Running `test.py` will run the tests

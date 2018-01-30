# README
This is the bluetooth component for the Bibliotech robot.

# Dependencies
```
sudo apt-get install python3-dev (Python 3 only)
sudo apt-get install python-dev (Python 2 only)

sudo apt-get install libbluetooth-dev
sudo pip install pybluez
```
# Usage
You'll want to run the bluetooth server on a new thread otherwise it'll **block** your current thread.

In the example below we're using Python's built-in [`threading`](https://docs.python.org/3/library/threading.html) library.

First import the `Thread` class using:
```py
from threading import Thread
```

Then create a Bluetooth server object and start the server on a new `Thread`:
```py
my_server = BluetoothServer("your_name_for_server", your_function)

thread = Thread(target=my_server.start_server)
thread.start()
```

You can send data to the client (Android app) using:
```py
my_server.send("string")
```

You can close the server permanently using:
```py
my_server.close_server()
```

Finally, the received data handling function should take **one** argument (which will be the received message string):
```py
def your_function(data):
	...
```

Take a look at `example.py` also if you need to.

# Steps to get it working properly
1. In the service file `/etc/systemd/system/dbus-org.bluez.service` change
> ExecStart=/usr/lib/bluetooth/bluetoothd

to
>ExecStart=/usr/lib/bluetooth/bluetoothd --compat

2. Restart the Bluetooth service:
```
sudo systemctl daemon-reload
sudo systemctl restart bluetooth
```
3. Run:
`sudo chmod 777 /var/run/sdp`

4. Add `robot` to the `bluetooth` group:
`sudo usermod -G bluetooth -a robot`

5. Change group of `/var/run/sdp` file:
`sudo chgrp bluetooth /var/run/sdp`

6. Make the changes stay after reboot:

  Create `/etc/systemd/system/var-run-sdp.path` and insert this:

```
[Unit]
Descrption=Monitor /var/run/sdp

[Install]
WantedBy=bluetooth.service

[Path]
PathExists=/var/run/sdp
Unit=var-run-sdp.service
```

And another file `/etc/systemd/system/var-run-sdp.service`:

```
[Unit]
Description=Set permission of /var/run/sdp

[Install]
RequiredBy=var-run-sdp.path

[Service]
Type=simple
ExecStart=/bin/chgrp bluetooth /var/run/sdp
```
**Finally**:
```
sudo systemctl daemon-reload
sudo systemctl enable var-run-sdp.path
sudo systemctl enable var-run-sdp.service
sudo systemctl start var-run-sdp.path
```

It **might** work now.
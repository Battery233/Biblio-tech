# README
This is the bluetooth component for the Bibliotech robot.

# Dependencies
```
sudo apt-get install python3-dev (Python 3 only)
sudo apt-get install python-dev (Python 2 only)

sudo apt-get install libbluetooth-dev
sudo pip install pybluez
```
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

# How it works
Currently, it's pretty crude and has an infinite while loop that runs a bluetooth server listening for connections.

It connects to a **single** client at a time and sends and receives data (as you'd expect).
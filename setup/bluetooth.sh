#!/bin/bash

USER=$1

apt-get install libbluetooth-dev -y
pip3 install pybluez

sed -i '/ExecStart=\/usr\/lib\/bluetooth\/bluetoothd/c\ExecStart=\/usr\/lib\/bluetooth\/bluetoothd --compat' /etc/systemd/system/dbus-org.bluez.service

systemctl daemon-reload
systemctl restart bluetooth

# Check whether directory exists, if not create it
mkdir -p /var/run/sdp
chmod 777 /var/run/sdp
usermod -G bluetooth -a $USER
chgrp bluetooth /var/run/sdp

cp ./setup/var-run-sdp.path /etc/systemd/system/var-run-sdp.path
cp ./setup/var-run-sdp.service /etc/systemd/system/var-run-sdp.service

systemctl daemon-reload
systemctl enable var-run-sdp.path
systemctl enable var-run-sdp.service
systemctl start var-run-sdp.path

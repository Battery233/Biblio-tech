#!/bin/bash

echo "Preparing for installation"
chmod -R +x ./setup
./setup/prepare.sh > /dev/null
echo "Installing software for QR codes recognition"
./setup/vision.sh > /dev/null
echo "Installing software for bluetooth communication and updating config files"
./setup/bluetooth.sh pi > /dev/null
echo "Done."

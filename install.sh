#!/bin/bash

apt-get update
apt-get install -y python3-pip
apt-get install -y libatlas-base-dev
pip3 install -r requirements.txt

echo "[Unit]
Description=LaserSaurApp
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory="$PWD"
ExecStart= "$PWD"/run.sh

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/lasaurapp.service

systemctl enable lasaurapp.service
systemctl start lasaurapp.service

echo "installation finished"
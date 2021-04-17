#!/bin/bash
sudo apt install authbind gunicorn python3-gunicorn

# Configure access to port 80
sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80
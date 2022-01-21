#!/bin/bash
authbind --deep gunicorn3 --bind 0.0.0.0:80 mainpage:app

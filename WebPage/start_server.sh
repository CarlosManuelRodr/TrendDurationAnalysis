#!/bin/bash
authbind --deep gunicorn --bind 0.0.0.0:80 mainpage:app
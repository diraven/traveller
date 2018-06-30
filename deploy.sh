#!/usr/bin/env bash

PROJECT_NAME="TBC"
LOG_INFO_PREFIX="==========!!!INFO!!! $PROJECT_NAME:"
LOG_ERROR_PREFIX="==========!!!ERROR!!! $PROJECT_NAME:"
LOG_DONE="$LOG_INFO_PREFIX DONE."

echo "$LOG_INFO_PREFIX Updating sources..."
git pull
echo "$LOG_DONE"

echo "$LOG_INFO_PREFIX Activating venv..."
source ../venv/bin/activate
echo "$LOG_DONE"

echo "$LOG_INFO_PREFIX Checking requirements..."
pip install -r requirements.txt
echo "$LOG_DONE"

echo "$LOG_INFO_PREFIX Migrating DB..."
./manage.py migrate
echo "$LOG_DONE"

echo "$LOG_INFO_PREFIX Collecting static files..."
./manage.py collectstatic --no-input
echo "$LOG_DONE"

echo "$LOG_INFO_PREFIX Restarting services..."
sudo supervisorctl restart crabot
sudo supervisorctl restart crabot_http
echo "$LOG_DONE"

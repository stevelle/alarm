#!/bin/bash -ex

# install dependencies
apt-get update
apt-get -y install build-essential python python-dev python-virtualenv supervisor git

# create a user to run the agent 
adduser --disabled-password --gecos "" loadmonitor
cd /home/loadmonitor

# fetch monitor source
git clone https://github.com/stevelle/loadmonitor.git 
cp loadmonitor/monitor.py .

# create a virtualenv and install dependencies
virtualenv venv
venv/bin/pip install -r loadmonitor/requirements.txt

chown -R loadmonitor:loadmonitor . 

# configure supervisor to run the service
cp loadmonitor/ext/supervisor/loadmonitor.conf /etc/supervisor/conf.d/
mkdir -p /var/log/loadmonitor
supervisorctl reread
supervisorctl update


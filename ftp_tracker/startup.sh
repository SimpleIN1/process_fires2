#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:/home/py-user/process_fire"


echo '------------1'
sleep 10 && /home/py-user/venv/bin/python /home/py-user/process_fire/ftp_tracker/run.py
#/home/py-user/process_fire/ftp_tracker/
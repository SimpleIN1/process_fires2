#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:/home/py-user/process_fire"


echo '------------'
/home/py-user/venv/bin/python /home/py-user/process_fire/process_event_pq/run.py
#/home/py-user/process_fire/process_event_pq/
#!/bin/bash

export PYTHONPATH="${PYTHONPATH}:/home/py-user/process_fire"

sleep 12 && /home/py-user/venv/bin/python /home/py-user/process_fire/loader_data/run.py

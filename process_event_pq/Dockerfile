FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -m -s /bin/bash py-user

USER py-user
WORKDIR /home/py-user/

RUN python -m venv venv
RUN /home/py-user/venv/bin/python -m pip install --upgrade pip

COPY ../requirements.txt /home/py-user/
RUN /home/py-user/venv/bin/pip install -r /home/py-user/requirements.txt

COPY --chown=py-user ../process_event_pq/. /home/py-user/process_fire/process_event_pq/
COPY ../base /home/py-user/process_fire/base
COPY ../config.py /home/py-user/process_fire/

#RUN mkdir -p /home/py-user/mondir
RUN chmod u+x ./process_fire/process_event_pq/startup.sh

#CMD ["ls"]
#CMD ["ls", "process_fire"]
#CMD ["ls", "process_fire/process_event_pq"]
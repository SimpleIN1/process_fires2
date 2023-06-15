FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -m -s /bin/bash py-user

RUN mkdir -p /home/py-user/mondir
RUN chmod ugo+rwx -R /home/py-user/mondir

USER py-user
WORKDIR /home/py-user/

RUN python -m venv venv
RUN /home/py-user/venv/bin/python -m pip install --upgrade pip

COPY ../requirements.txt /home/py-user/
RUN /home/py-user/venv/bin/pip install -r /home/py-user/requirements.txt

COPY --chown=py-user ../ftp_tracker/. /home/py-user/process_fire/ftp_tracker/
COPY ../base /home/py-user/process_fire/base
COPY ../config.py /home/py-user/process_fire/

RUN chmod u+x ./process_fire/ftp_tracker/startup.sh

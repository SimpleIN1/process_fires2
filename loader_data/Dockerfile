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

COPY --chown=py-user ../loader_data/. /home/py-user/process_fire/loader_data/
COPY ../base /home/py-user/process_fire/base
COPY ../config.py /home/py-user/process_fire/

#ENV db_name=db_fire
#ENV db_user=user
#ENV db_password=1234
#ENV db_port=5432
#ENV db_host=172.17.0.2

RUN mkdir -p /home/py-user/process_fire/loader_data/data/
RUN chmod u+x ./process_fire/loader_data/startup.sh

#CMD ["ls", "process_fire/"]
#CMD ["ls", "process_fire/process_event_pq"]
#CMD ["/bin/bash", "-c", "./process_fire/loader_data/startup.sh"]
sudo docker volume create postgres-db-volume

sudo docker run -d --name postgres-fire -v postgres-db-volume:/var/lib/postgresql/data/ \
-e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=db_fire -e POSTGRES_USER=user -p 5432:5432 postgis/postgis

sudo docker build -t loader_data -f loader_data/Dockerfile .
sudo docker run -d -v {abpath}loader_data/data:/home/py-user/loader_data/data/ loader_data

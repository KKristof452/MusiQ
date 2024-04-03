#!/bin/sh
docker container stop fastapi_container
docker container rm fastapi_container
docker build -t fastapi ./ # &> docker.log
# docker run -d --name fastapi_container -p 80:80 --mount type=bind,source=./Data,target=/code/Data fastapi
docker run -d -e ADMIN_USER=testuser -e ADMIN_PASS=testpass --name fastapi_container -p 80:80 -v ./Data:/Backend/Data fastapi

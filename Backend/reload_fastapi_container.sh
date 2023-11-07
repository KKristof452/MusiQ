#!/bin/sh
docker container stop fastapi_container
docker container rm fastapi_container
docker build -t fastapi ./
# docker run -d --name fastapi_container -p 80:80 --mount type=bind,source=./Data,target=/code/Data fastapi
docker run -d --name fastapi_container -p 80:80 -v ./Data:/code/Data fastapi

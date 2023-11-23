FROM python:3.12

WORKDIR /Backend

COPY ./requirements.txt /Backend/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /Backend/requirements.txt

RUN mkdir logs

RUN mkdir Data

RUN mkdir Data/Audio

RUN mkdir Data/Objects

COPY ./Fastapi /Backend/Fastapi

COPY ./Utility /Backend/Utility

CMD ["uvicorn", "Fastapi.musiq_api:app", "--host", "0.0.0.0", "--port", "80"]

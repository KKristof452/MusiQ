FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./Fastapi /code/Fastapi

CMD ["uvicorn", "Fastapi.musiq_api:app", "--host", "0.0.0.0", "--port", "80"]

FROM python:3.12

WORKDIR /Backend

COPY ./requirements.txt /Backend/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /Backend/requirements.txt

RUN mkdir logs

RUN mkdir Data

RUN mkdir Data/Audio

RUN mkdir Data/Objects

RUN git clone https://github.com/acrcloud/acrcloud_sdk_python.git ./ACRCloud/acrcloud_sdk_python/ \
    && cd ACRCloud/acrcloud_sdk_python/raspberrypi/aarch64/python3/ \
    && python setup.py install \
    && cd /Backend

COPY ./Fastapi /Backend/Fastapi

COPY ./Cyanite /Backend/Cyanite

COPY ./ACRCloud /Backend/ACRCloud

COPY ./Utility /Backend/Utility

COPY ./debug /Backend/debug

CMD ["uvicorn", "Fastapi.musiq_api:app", "--host", "0.0.0.0", "--port", "80"]

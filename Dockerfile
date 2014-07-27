FROM python:3

ADD . /code/
WORKDIR /code/
RUN pip install -r requirements.txt
CMD make update DATA_DIR=/data/

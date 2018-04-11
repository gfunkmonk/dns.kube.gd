FROM python:3.6
LABEL maintainer="Marco Ceppi <marco@ceppi.net>"

WORKDIR /code

COPY requirements.txt /code

RUN pip install -r requirements.txt

COPY server.py LICENSE /code/

EXPOSE 10053

CMD ["python3", "server.py"]

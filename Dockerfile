FROM python:3.6
LABEL maintainer="Marco Ceppi <marco@ceppi.net>"

EXPOSE 10053

CMD ["python3", "server.py"]

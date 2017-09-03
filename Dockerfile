FROM python:3.6.2-alpine
MAINTAINER Paul Logston <code@logston.me>

WORKDIR /srv

COPY requirements.txt requirements.txt
COPY server.py server.py
COPY wsj_to_rss.py wsj_to_rss.py 

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["/usr/local/bin/python", "server.py", "-p", "8000"]


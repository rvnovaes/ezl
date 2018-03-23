FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install unzip wget -y

WORKDIR /app

RUN wget https://github.com/sosedoff/pgweb/releases/download/v0.9.10/pgweb_linux_amd64.zip
RUN unzip pgweb_linux_amd64.zip
RUN mv pgweb_linux_amd64 /usr/bin/pgweb
RUN chmod +x /usr/bin/pgweb

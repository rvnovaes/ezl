FROM python:3.6

ARG requirements_file

RUN apt-get update && apt-get install -y \
    postgresql-contrib \
    freetds-dev \
 && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /app /var/log/ezl/etl/
WORKDIR /app
ADD requirements/ .
RUN ls -l
RUN pip install --upgrade pip
RUN pip install -r $requirements_file

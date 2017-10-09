FROM python:3

RUN apt-get update && apt-get install -y \
    postgresql-contrib \
    freetds-dev \
 && rm -rf /var/lib/apt/lists/*


RUN mkdir -p /app /var/log/ezl/etl/
WORKDIR /app
ADD requirements.txt /app/

RUN pip install -r requirements/production.txt
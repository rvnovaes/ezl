#!/bin/bash
# NOTE: Esse script deve ser executado dentro da raiz do repositório
# Pega a pasta do repositório
PROJECT_WORKDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DB_NAME=ezl
DB_USER=ezl
DB_PASSWORD=ezl
S3_LOCATION=`date +s3://ezl-backup/postgres/%Y/%m/%d/`
AWS_ACCESS_KEY=AKIAJINMQ4YYIYXTH62A
AWS_SECRET_KEY=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
TIME=`date +%Y-%m-%d-%H%M`
TAR_FILENAME=$DB_NAME-$TIME.tar.gz
BACKUP_WORKDIR=/dados/ezl/backup/_db_backup

echo "Iniciando backup para $BUCKET às $(date)";

sudo pip install awscli

cd $PROJECT_WORKDIR
rm -rf $BACKUP_WORKDIR || true
mkdir $BACKUP_WORKDIR

# Configura a linha de comando da aws
aws configure set aws_access_key_id $AWS_ACCESS_KEY
aws configure set aws_secret_access_key $AWS_SECRET_KEY
aws configure set default.region us-east-1

# Cria o backup na pasta $BACKUP_WORKDIR
docker-compose run -v $BACKUP_WORKDIR:/tmp/ db bash -c "PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h db $DB_NAME -f /tmp/ezl.sql"

cd $BACKUP_WORKDIR
tar -czf $TAR_FILENAME ezl.sql

aws s3 cp $TAR_FILENAME $S3_LOCATION

echo "Backup finalizado para $BUCKET às $(date)"
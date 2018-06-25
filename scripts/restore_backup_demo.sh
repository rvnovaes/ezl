#!/bin/bash
/etc/init.d/postgresql restart
dropdb -Uezl demo
createdb -Uezl demo
psql -U ezl demo < /opt/backup/demo.sql


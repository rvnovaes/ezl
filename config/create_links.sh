#!/usr/bin/env bash

# datadog
ln -s /opt/easy_lawyer_django/config/datadog/nginx.yaml /etc/dd-agent/conf.d

# nginx
ln -s /opt/easy_lawyer_django/config/nginx/nginx.conf /etc/nginx/sites-enabled

# supervisor
ln -s /opt/easy_lawyer_django/config/supervisor/supervisord.conf /etc/supervisor
ln -s /opt/easy_lawyer_django/config/supervisor/ezl.conf /etc/supervisor/conf.d

#!/usr/bin/env bash

# Datadog
ln -s /opt/easy_lawyer_django/config/datadog/nginx.yaml /etc/dd-agent/conf.d


# Nginx
ln -s /opt/easy_lawyer_django/config/nginx/nginx.conf /etc/nginx/sites-enabled
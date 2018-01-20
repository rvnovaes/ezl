FROM certbot/certbot

RUN touch /var/log/cron.log
RUN echo '0 1 * * * certbot renew >> /var/log/cron.log' > /etc/crontabs/root
CMD crond && tail -f /var/log/cron.log
ENTRYPOINT []

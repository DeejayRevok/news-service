FROM logstash:7.6.0
COPY event-service.conf /usr/local/etc/event-service.conf
CMD ["logstash", "-f", "/usr/local/etc/event-service.conf"]
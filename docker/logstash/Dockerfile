FROM logstash:7.6.0
COPY news-service.conf /usr/local/etc/news-service.conf
CMD ["logstash", "-f", "/usr/local/etc/news-service.conf"]
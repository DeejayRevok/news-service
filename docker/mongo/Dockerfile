FROM mongo:latest

RUN apt-get update && apt-get install wget
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN apt-get install apt-transport-https -y
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list
RUN apt-get update && apt-get install metricbeat

COPY mongodb.yml /etc/metricbeat/modules.d/mongodb.yml
COPY metricbeat.yml /etc/metricbeat/metricbeat.yml

COPY docker-entrypoint.sh /usr/local/bin/



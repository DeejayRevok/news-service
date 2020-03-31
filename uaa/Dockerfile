FROM python:3.8-buster
COPY ./uaa /app/uaa
COPY ./event-service-lib /app/event-service-lib
WORKDIR /app/event-service-lib

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python setup.py bdist_wheel
RUN pip install dist/event_service_lib-0.0.1-py3-none-any.whl

WORKDIR /app

RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN apt-get install apt-transport-https -y
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list
RUN apt-get update && apt-get install metricbeat && apt-get install default-libmysqlclient-dev

RUN pip install --upgrade pip
RUN pip install -r uaa/requirements.txt

COPY ./uaa/tools_config/metricbeat.yml /etc/metricbeat/metricbeat.yml

EXPOSE 8081
CMD service metricbeat start && export PYTHONPATH=${PYTHONPATH}:/app && python ./uaa/webapp/main.py -p DOCKER
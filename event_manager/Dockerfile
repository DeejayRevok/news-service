FROM python:3.8-buster
COPY ./event_manager /app/event_manager
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
RUN apt-get update && apt-get install metricbeat

RUN pip install --upgrade pip
RUN pip install -r event_manager/requirements.txt

COPY ./event_manager/tools_config/metricbeat.yml /etc/metricbeat/metricbeat.yml

EXPOSE 8080
CMD service metricbeat start && export PYTHONPATH=${PYTHONPATH}:/app && python ./event_manager/webapp/main.py -p DOCKER
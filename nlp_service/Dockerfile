FROM python:3.8-buster
COPY ./nlp_service /app/nlp_service
COPY ./news_service_lib /app/news_service_lib
COPY ./stanza_resources /root/stanza_resources

WORKDIR /root/stanza_resources
RUN cat es_model_part* > es_model.zip
RUN unzip es_model.zip
RUN rm es_model*

WORKDIR /app/news_service_lib
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python setup.py bdist_wheel
RUN pip install dist/news_service_lib-0.0.1-py3-none-any.whl

WORKDIR /app

RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN apt-get install apt-transport-https -y
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list
RUN apt-get update && apt-get install metricbeat

RUN pip install --upgrade pip
RUN pip install -r nlp_service/requirements.txt

COPY ./nlp_service/tools_config/metricbeat.yml /etc/metricbeat/metricbeat.yml

EXPOSE 8082
CMD service metricbeat start && export PYTHONPATH=${PYTHONPATH}:/app && python ./nlp_service/webapp/main.py -p DOCKER
FROM python:3.8-buster
COPY ./news_manager /app/news_manager
COPY ./news_service_lib /app/news_service_lib
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
RUN pip install -r news_manager/requirements.txt

COPY ./news_manager/tools_config/metricbeat.yml /etc/metricbeat/metricbeat.yml

EXPOSE 8080
CMD service metricbeat start && export PYTHONPATH=${PYTHONPATH}:/app && python ./news_manager/webapp/main.py -p DOCKER
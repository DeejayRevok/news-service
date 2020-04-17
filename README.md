# News Service
News service

![News Service](https://github.com/DeejayRevok/news-service/workflows/News%20Service/badge.svg)
[![codecov](https://codecov.io/gh/DeejayRevok/news-service/branch/develop/graph/badge.svg?token=1EEM8TD8JC)](https://codecov.io/gh/DeejayRevok/news-service)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=DeejayRevok_news-service&metric=alert_status)](https://sonarcloud.io/dashboard?id=DeejayRevok_news-service)

## Installation and running
  
### Local with external services in docker
Requirements:
  - Virtualenv
  - Python 3.7
  - Docker

#### Run external services:
Inside the docker folder of the application folder run:
```
docker-compose -f docker-compose-local.yml up -d
```

#### Set up the environment:
```
virtualenv -p python3.7 venv
source venv/bin/activate
```

#### Install the application library:
Inside the application folder run:
```
export PYTHONPATH={FULL_PATH_TO_APPLICATION_FOLDER}
cd news_service_lib
pip install -r requirements.txt
python setup.py bdist_wheel
pip install dist/news_service_lib-0.0.1-py3-none-any.whl
```

#### UAA
Inside the application folder run:
```
export JWT_SECRET={JWT_TOKEN_SECRET}
export PYTHONPATH={FULL_PATH_TO_APPLICATION_FOLDER}
pip install -r uaa/requirements.txt
python uaa/webapp/main.py -p local
```

#### NLP celery worker
Inside the application folder run:
```
export JWT_SECRET={JWT_TOKEN_SECRET}
export PYTHONPATH={FULL_PATH_TO_APPLICATION_FOLDER}
pip install -r nlp_service/requirements_celery.txt
python nlp_service/nlp_celery_worker/celery_app.py -p local
```
#### NLP flower service
Inside the application folder run:
```
export PYTHONPATH={FULL_PATH_TO_APPLICATION_FOLDER}
pip install -r nlp_service/requirements_flower.txt
python nlp_service/nlp_celery_worker/flower_app.py -p local
```

#### NLP service
Inside the application folder run:
```
export PYTHONPATH={FULL_PATH_TO_APPLICATION_FOLDER}
pip install -r nlp_service/requirements.txt
python nlp_service/webapp/main.py -p local
```

#### News manager
Inside the application folder run:
```
export JWT_SECRET={JWT_TOKEN_SECRET}
export PYTHONPATH={FULL_PATH_TO_APPLICATION_FOLDER}
pip install -r news_manager/requirements.txt
python news_manager/webapp/main.py -p local
```

### Docker
Requirements:
  - Docker
  
Inside the application docker folder run:
```
docker-compose up -d
```

### Kubernetes
Requirements:
  - Kubernetes
  - Kubernetes cluster system (e.g docker-desktop, minikube)
  - Ingress enabled

Inside the kubernetes folder of the application folder run:
```
kubectl apply -f news-service-k8s.yaml
```

## Usage for local and docker installations
- News manager: In your webbrowser navigate to http://localhost:8080/v1/api/docs/ui
- UAA: In your webbrowser navigate to http://localhost:8081/v1/api/docs/ui
- NLP service: In your webbrowser navigate to http://localhost:8082/v1/api/docs/ui
- Flower: In your webbrowser navigate to http://localhost:5555
- Kibana: In your webbrowser navigate to http://localhost:5671
- Rabbit management: In your webbrowser navigate to http://localhost:15672 (guest:guest)


## Usage for kubernetes installation
Before navigating to the services you should discover your cluster ip.
- News manager: In your webbrowser navigate to http://{CLUSTER_IP}/manager/v1/api/docs/ui
- UAA: In your webbrowser navigate to http://{CLUSTER_IP}/uaa/v1/api/docs/ui
- NLP service: In your webbrowser navigate to http://{CLUSTER_IP}/nlp/v1/api/docs/ui
- Flower: In your webbrowser navigate to http://{CLUSTER_IP}/flower
- Kibana: In your webbrowser navigate to http://{CLUSTER_IP}/kibana
- Rabbit management: In your webbrowser navigate to http://{CLUSTER_IP}/rabbit (guest:guest)

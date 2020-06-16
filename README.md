# News Service
News service parent repository

## Installation and running
  
#### Run local dev services:
Inside the docker folder run:
```
docker-compose -f docker-compose-local.yml up -d
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

# News Service
News service repository

## Installation and running

### Kubernetes
Requirements:
  - Kubernetes
  - Kubernetes cluster system (e.g docker-desktop, minikube)
  - Ingress enabled
  - Helm

- Inside the root folder run:
```
make build_news_service_chart
```
- Install the required secrets into the kubernetess namespace:
```
kubectl apply -f {SECRETS_FILE_PATH} -n {NAMESPACE_NAME}
```
- Install the chart:
```
helm install {RELEASE_NAME} .\news-service-{CHART_VERSION}.tgz --values .\helm\values\news-service\local\iam.yaml 
--values .\helm\values\news-service\local\monitor.yaml --values .\helm\values\news-service\local\news-discovery.yaml --values .\helm\valu
es\news-service\local\news-manager.yaml --values .\helm\values\news-service\local\nlp-service.yaml --values .\helm\values\news-service\lo
cal\rabbitmq.yaml --values .\helm\values\news-service\local\redis.yaml --values .\helm\values\news-service\local\search-engine.yaml -n {NAMESPACE_NAME}
```

## Usage for kubernetes installation
Before navigating to the services you should discover your cluster ip.
- News manager base path: https://{CLUSTER_IP}/news-manager
- IAM base path: https://{CLUSTER_IP}/iam
- Search engine base path: http://{CLUSTER_IP}/search
- Kibana: In your webbrowser navigate to http://{CLUSTER_IP}/monitor/kibana

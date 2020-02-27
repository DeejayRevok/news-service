# Event Service
Social events service

## Installation
### Docker
- Requirements:
  - Docker
  
Inside the application folder run:
```
docker-compose up -d
```
  
### Local
- Requirements:
  - Virtualenv
  - Python 3.7
  - MongoDB
  
Set up the environment:
```
virtualenv -p python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

Change the application configuration:
  - Go to the application config file (config.ini) and modify the host parameter of the MONGO section with 127.0.0.1. If your mongo service is running in a different port than the default one change also the port parameter of the MONGO section.

Run the application:
```
export PYTHONPATH={FULL_PATH_TO_APPLICATION_FOLDER}
python webapp/main.py
```

Run tests:
```
python -m unittest discover -v tests
```

## Usage
In your webbrowser navigate to http://localhost:8080/v1/api/docs/ui

In order to test the Event list endpoint, take into account that the format of the date should be the same as the date format of the provided XML (%Y-%m-%dT%H:%M:%S)

# Documentation

Aiohttp has been choosed as main web framework for the application. It is an asynchronous HTTP server integrated inside the aio-libs framework. This framework has a great support community and a lot of different libraries for multiple tools. Aiohttp provides an improved asynchronous and concurrent processing. This framework is so flexible since it provides multiple ways of implement and extend its functionalities.

In order to stay up to date with the events from the external source, an asynchronous cron has been created. This cron has been created using the aiocron library.

As a UI for the API, swagger is my choice. It provides an easy way to interact with the different aplication endopoints. This has been integrated using the aiohttp-apispec library which is integrated within the aiohttp framework.

The DBMS system used to store the fetched events with the cron is MongoDB. MongoDB provides an easy way of storing non structured data. It has been choosed since maybe it will be required to fetch events from different sources. Also, as the performance is critical for this test, with MongoDB it is not needed to map the input XML events into objects. With this approach the xml events are converted to python dictionaries which can be stored directly inside MongoDB. When querying events, MongoDB returns them in a dictionary representation wich can be converted directly to JSON format in order to send in the REST endpoint RESPONSES. The python library used to communicate with MongoDB is pymongo. In order to create integration tests with mongodb the mongomock library has been used.

All the code has been developed trying to provide flexibility for integrating new pieces and tools:
  - cron: Creating new crons consists on defining its implementation extending from the base class and fill its definition specifying the expression, the implementation class, the source adapters (if needed) and the implementation required parameters.
  - adapters: The fetch events process is performed by an adapters system. Fetching from new sources consists on implement the fetch and the adapt methods extending from the base adapters class.
  - storage: As described above the DBMS choosed is MongoDB, but adding new DBMS to the application consists only in implementing the Storage interface and the StorageFilters query parsing. The storage configuration parameters like host, port, password, username or password are managed in the configuration file of the application. Switching between different storage systems consists only in modifying the storage field of the configuration file.
  
There are many ways of scaling this app:
  - Gunicorn web workers: The app can be easy deployed using gunicorn which runs multiple applications in the host machine. This provides parallel processing of requests. The aiohttp official documentation recommends multiple ways of deploying the applications in production environments, one of them is nginx+gunicorn and the recommended number of workers is 2*cpu's + 1. With this approach it is possible to scale the application increasing the number of cores of the host machine. This approach implies the introduction of distributed process locks in order to manage concurrent and duplicated tasks like the crons executions. Also it is possible to integrate the gunicorn runner inside the application in order to run the duplicated tasks in separate processes.
  - Docker: The application has been dockerized in order to provide an easy deploy system. This approach also provides new scaling possibilities. It is possible to run multiple pods of the application in different docker containers. With this approach the scaling could be made with multiple hosts making clusters with container orchestrator systems like OpenShift. This approach implies the introduction of distributed locks using external tools like redis in order to manage the concurrent and duplicated tasks between the different pods.

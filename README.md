# News Service
News service

![News Service](https://github.com/DeejayRevok/news-service/workflows/News%20Service/badge.svg)
[![codecov](https://codecov.io/gh/DeejayRevok/event-service/branch/master/graph/badge.svg?token=1EEM8TD8JC)](https://codecov.io/gh/DeejayRevok/event-service)

## Installation
### Docker
- Requirements:
  - Docker
  
Inside the application docker folder run:
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

In order to test the news list endpoint, take into account that the format of the date should be the same as the date format of the provided XML (%Y-%m-%dT%H:%M:%S)

FROM python:3.8-buster
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
CMD export PYTHONPATH=${PYTHONPATH}:/app && python ./webapp/main.py
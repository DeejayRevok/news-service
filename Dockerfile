FROM python:3.7-slim
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
CMD export PYTHONPATH=${PYTHONPATH}:/app && python ./webapp/main.py
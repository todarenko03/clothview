FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install --default-timeout=1000 -r requirements.txt
COPY . /app
EXPOSE 8000
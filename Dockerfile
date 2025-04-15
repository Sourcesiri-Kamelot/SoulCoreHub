FROM python:3.9-slim

WORKDIR /SoulCoreHub
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python3", "soul_heartbeat.py"]

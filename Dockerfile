FROM python:3.11-slim

ENV WORKDIR /app

WORKDIR ${WORKDIR}

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

CMD 
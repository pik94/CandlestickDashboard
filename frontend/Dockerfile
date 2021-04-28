FROM python:3.8-slim

ENV DEBUG=False
ENV HOST=0.0.0.0
ENV PORT=8050
ENV BACKEND_API_URL=http://0.0.0.0:8000
ENV POLYGON_API_KEY=api_key
ENV POLYGON_BATCH_LIMIT=50000
ENV LOG_DIR=logs
ENV TICKERS=MSFT,AAPL

EXPOSE 8050
WORKDIR /app
VOLUME /app/logs

COPY . /app
RUN python3 -m pip install -r requirements.txt

ENTRYPOINT python3 run.py --debug $DEBUG --host $HOST --port $PORT

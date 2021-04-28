FROM python:3.8-slim

ENV DEBUG=False
ENV DB_TYPE=postgresql
ENV DB_HOST=0.0.0.0
ENV DB_PORT=5432
ENV DB_USER=db_user
ENV DB_PASSWORD=db_password
ENV DB_NAME=finacial_data
ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=9
ENV LOG_DIR=logs
ENV CRLF_TOKEN=abc
ENV FLASK_APP=api:create_app()

EXPOSE 8000
WORKDIR /app
VOLUME /app/logs

COPY . /app
RUN python3 -m pip install -r requirements.txt

ENTRYPOINT flask db upgrade && gunicorn "api:create_app(debug=$DEBUG)" -b $HOST:$PORT -w $WORKERS -t 120
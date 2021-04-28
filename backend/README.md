## Description
This is an API to manipulate financial data.

## Deployment
### Production
#### Docker
You may build an image and a container manually.
1. Build an image:
    ```shell script
    docker build -t financial_api:<your_version> .
    ```

2. Create and run a container passing environment variables. To see all list 
    of possible env variables check a corresponding wiki [page](https://github.com/pik94/CandlestickDashboard/wiki/Backend-environment-variables).
    ```
    docker container run -d --name financial_api \
    --mount type=bind,source=/tmp/logs/api,target=/app/logs \
    -e DB_TYPE=<db_type> \
    -e DB_HOST=<db_host> \
    -e DB_USER=<db_user> \
    -e DB_PASSWORD=<db_password> \
    -e DB_NAME=<db_database> \
    -e HOST=<api_host> \
    -e PORT=<api_port> \
    -e WORKERS=3 \
    -e CRLF_TOKEN=123 \
    -p <host_port>:<api_port> \
    financial_api:<your_version>
    ```

### Debug
#### Manual
1. Prepare a python environment: Create virtualenv and activate it:
    ```shell script
    python3.8 -m venv venv && source ./venv/bin/activate
    pip install -r requirements.txt
    ```
2. Setup several environment variables modifying a [config](https://github.com/pik94/CandlestickDashboard/blob/master/backend/config) 
    file or creating your own. Make sure that the given user and password has 
    right permissions. To see all list of possible variables in a config, please, check 
    a wiki a corresponding wiki [page](https://github.com/pik94/CandlestickDashboard/wiki/Backend-environment-variables).
   
3. When debugging the default flask server is used. To run it with default parameters, type:
    ```shell script
    export FLASK_APP="api:create_app('config', debug='True')"
    flask run --host localhost --port 8000
    ```

## Description
This is a dashboard to plot candlestick data.

## Deployment
### Production
#### Docker
You may build an image and a container manually.
1. Build an image:
    ```shell script
    docker build -t candlestick_dashboard:<your_version> .
    ```

2. Create and run a container passing environment variables. To see all list 
    of possible env variables check a corresponding wiki [page](https://github.com/pik94/CandlestickDashboard/wiki/Frontend-environment-variables).
    ```
    docker container run -d --name candlestick_dashboard \
    --mount type=bind,source=/tmp/logs/api,target=/app/logs \
    -e HOST=<dash_board_host> \
    -e PORT=<db_host> \
    -e BACKEND_API_URL=<backend_api_url> \
    -e POLYGON_API_KEY=<polygon_api_key> \
    -e POLYGON_BATCH_LIMIT=50000 \
    -e TICKERS=MSFT,AAPL \
    -p <host_port>:<port> \
    candlestick_dashboard:<your_version>
    ```

### Debug
#### Manual
1. Prepare a python environment: Create virtualenv and activate it:
    ```shell script
    python3.8 -m venv venv && source ./venv/bin/activate
    pip install -r requirements.txt
    ```
2. Setup several environment variables modifying a [config](https://github.com/pik94/CandlestickDashboard/blob/master/frontend/config) 
    file or creating your own. Make sure that the given user and password has 
    right permissions. To see all list of possible variables in a config, please, check 
    a wiki a corresponding wiki [page](https://github.com/pik94/CandlestickDashboard/wiki/Frontend-environment-variables).
   
3. When debugging the default flask server is used. To run it with default parameters, type:
    ```shell script
    python run.py --debug True --config config
    ```

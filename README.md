## Description 
This is a service which plots candlestick market data.
To read more about its components, please, check [backend](https://github.com/pik94/CandlestickDashboard/blob/master/backend/README.md) and 
[frontend](https://github.com/pik94/CandlestickDashboard/blob/master/frontend/README.md) readme files. 

## Running
You need to build and run this service using a docker-compose [file](https://github.com/pik94/CandlestickDashboard/blob/master/docker-compose.yml). Edit this setting [polygon.io](https://polygon.io/) API key and change host ports if there are conflits on your host.
1. Build:
    ```shell script
    docker-compose build
    ```

2. Run:
    ```shell script
    docker-compose up -d
    ```

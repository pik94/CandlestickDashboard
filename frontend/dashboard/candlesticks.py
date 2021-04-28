import datetime as dt
import logging
import os
from typing import Callable, Dict, List, Optional, Union

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from polygon import RESTClient
import requests
import waitress

from dashboard.utils import DateTimeHelper, generate_id


logger = logging.getLogger(__name__)


class CandlestickApp:
    ticker_dropdown_id = generate_id()
    bar_graph_id = generate_id()
    date_range_id = generate_id()
    plot_button_id = generate_id()

    def __init__(self, app: Optional[dash.Dash] = None):
        self._backend_api_url = os.environ['BACKEND_API_URL'].strip('/')
        self._polygon_api_key = os.environ['POLYGON_API_KEY']
        self._batch_limit = int(os.environ['POLYGON_BATCH_LIMIT'])
        self.tickers = os.environ['TICKERS'].strip(',').split(',')

        self.app = app or dash.Dash(__name__)
        self.app.layout = self.get_layout
        self.set_callbacks()

    def run(self, debug: Optional[bool] = True, host: Optional[str] = 'localhost', port: Optional[int] = 8050):
        if debug:
            self.app.run_server(host=host, port=port)
        else:
            waitress.serve(self.app.server, host=host, port=port)

    def get_layout(self):
        """Create a layout for laying out of components of an application."""

        ticker_dropdown = self._get_ticker_dropdown()
        date_range = self._get_date_range()
        candlestick_chart = self._get_candlestick_chart()
        plot_button = self._get_plot_button()

        layout = html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(ticker_dropdown, width=2, align='center', className='ml-1 mt-1'),
                        dbc.Col(date_range, width=3, align='center', className='mt-1'),
                        dbc.Col(plot_button, width=2, align='center', className='mt-1'),
                    ]
                ),
                dbc.Row([dbc.Col(candlestick_chart)]),
            ]
        )
        return layout

    def register_callback(
        self,
        callback_function: Callable,
        inputs: List[Input],
        output: Union[Output, List[Output]],
        states: Optional[List[State]] = None,
    ) -> None:
        """Register a callback for an application."""

        if states is None:
            states = []

        self.app.callback(output, inputs, states)(callback_function)

    def _get_ticker_dropdown(self) -> dcc.Dropdown:
        component = dcc.Dropdown(
            id=self.ticker_dropdown_id,
            options=[{'label': ticker, 'value': ticker} for ticker in self.tickers],
            placeholder='Select a ticker...',
        )

        return component

    def _get_date_range(self) -> dcc.DatePickerRange:
        today = dt.date.today()
        component = dcc.DatePickerRange(
            id=self.date_range_id,
            min_date_allowed=dt.date(1995, 8, 5),
            start_date=today - dt.timedelta(days=1),
            end_date=today,
            display_format='D/M/YYYY',
        )
        return component

    def _get_plot_button(self) -> html.Button:
        button = dbc.Button('Success', id=self.plot_button_id, color='success')
        return button

    def _get_candlestick_chart(self) -> dcc.Graph:
        component = dcc.Graph(id=self.bar_graph_id, style={'width': '90vw', 'height': '90vh'})
        return component

    def set_callbacks(self) -> None:
        """Set all callbacks of an application inside this method."""

        self._set_generate_bar_graph_callback()

    def _set_generate_bar_graph_callback(self):
        inputs = [
            Input(self.plot_button_id, 'n_clicks'),
        ]
        states = [
            State(self.ticker_dropdown_id, 'value'),
            State(self.date_range_id, 'start_date'),
            State(self.date_range_id, 'end_date'),
        ]
        output = Output(self.bar_graph_id, 'figure')
        self.register_callback(self._generate_candlestick_chart, inputs, output, states)

    def _generate_candlestick_chart(self, _, ticker: str, from_: str, to: str):
        context = dash.callback_context
        if not context.triggered:
            return go.Figure()

        if context.triggered[0]['value'] is None:
            return go.Figure()

        if not ticker:
            return go.Figure()

        from_ = DateTimeHelper.date_to_datetime(DateTimeHelper.string_to_date(from_))
        to = DateTimeHelper.date_to_datetime(DateTimeHelper.string_to_date(to))
        to += dt.timedelta(hours=23, minutes=59, seconds=59)
        logger.info(f'Creating a candlestick for ticker={ticker}, from={from_}, to={to}')
        if from_ > to:
            logger.warning(f'Incorrect user input: from={from_} > to={to}')
            return go.Figure()

        url = f'{self._backend_api_url}/assets/candlesticks/{ticker}/{from_.date()}/{to.date()}'
        logger.debug(f'Requesting to db by url={url}')
        response = requests.get(url)
        if response.status_code != 200:
            logger.warning(f'Cannot get data from backend by url={url}')
            return go.Figure()

        # If there are data in inner data storage, use it to plot a candlestick graph.
        # Data from the storage may be incomplete, therefore, download missing data from extra sources
        # and upload them to the storage.
        # If there are no any data in the storage for the given date range, make full downloading and upload them to
        # the storage.

        db_candlesticks = response.json()
        if db_candlesticks.get('results'):
            db_candlesticks = db_candlesticks['results']
            datetime_candlestick_mapping = {
                DateTimeHelper.string_to_datetime(candlestick['datetime']): candlestick
                for candlestick in db_candlesticks['data']
            }

            missing_data = []
            db_min_datetime = DateTimeHelper.string_to_datetime(db_candlesticks['min_datetime'])
            if from_ < db_min_datetime:
                logger.debug(f'Detect missing data between {from_} and {db_min_datetime}')
                data = self._download_data(ticker, from_, db_min_datetime)
                missing_data.extend(data)
                logger.debug(f'Downloaded {len(data)} missing data')

            db_max_datetime = DateTimeHelper.string_to_datetime(db_candlesticks['max_datetime'])
            if to > db_max_datetime:
                logger.debug(f'Detect missing data between {db_max_datetime} and {to}')
                data = self._download_data(ticker, db_max_datetime, to)
                missing_data.extend(data)
                logger.debug(f'Downloaded {len(data)} missing data')

            if missing_data:
                url = f'{self._backend_api_url}/assets'
                logger.debug(f'Upload missing data by url={url}')
                response = requests.post(url, json={'ticker': ticker, 'candlesticks': missing_data})
                if response.status_code != 200:
                    logger.error('Cannot upload missing data')

                missing_data = {
                    DateTimeHelper.string_to_datetime(candlestick['datetime']): candlestick
                    for candlestick in missing_data
                }

                datetime_candlestick_mapping.update(missing_data)
        else:
            logger.debug(f'No stored data for ticker={ticker}, from {from_} to {to}. Start downloading')
            new_candlesticks = self._download_data(ticker, from_, to)
            if not new_candlesticks:
                return go.Figure()

            url = f'{self._backend_api_url}/assets'
            logger.debug(f'Upload new data by url={url}')
            response = requests.post(url, json={'ticker': ticker, 'candlesticks': new_candlesticks})
            if response.status_code != 201:
                logger.error('Cannot upload new data')

            datetime_candlestick_mapping = {
                DateTimeHelper.string_to_datetime(candlestick['datetime']): candlestick
                for candlestick in new_candlesticks
            }

        graph_data = dict(sorted(datetime_candlestick_mapping.items()))

        graph = go.Candlestick(
            x=list(graph_data.keys()),
            open=[candlestick['open_price'] for candlestick in graph_data.values()],
            close=[candlestick['close_price'] for candlestick in graph_data.values()],
            high=[candlestick['high_price'] for candlestick in graph_data.values()],
            low=[candlestick['low_price'] for candlestick in graph_data.values()],
        )
        fig = go.Figure(data=graph)
        fig.update_layout(xaxis_rangeslider_visible=True, yaxis_title='Price')
        return fig

    def _download_data(self, ticker: str, from_: dt.datetime, to: dt.datetime) -> List[Dict[str, Union[float, str]]]:
        """Download data from an extra source. Now, polygon.io is supported."""

        days = self._batch_limit // 60 // 24
        start_date_ = from_
        end_date_ = min(start_date_ + dt.timedelta(days=days), to)

        data = []
        with RESTClient(self._polygon_api_key) as api_client:
            while start_date_ != to:
                limit = int((end_date_ - start_date_).total_seconds() // 60)
                response = api_client.stocks_equities_aggregates(
                    ticker=ticker,
                    from_=DateTimeHelper.date_to_string(start_date_.date()),
                    to=DateTimeHelper.date_to_string(end_date_.date()),
                    multiplier=1,
                    timespan='minute',
                    limit=limit,
                )

                data.extend(
                    [
                        {
                            'open_price': candlestick['o'],
                            'close_price': candlestick['c'],
                            'low_price': candlestick['l'],
                            'high_price': candlestick['h'],
                            'volume': candlestick['v'],
                            'weighted_volume': candlestick['vw'],
                            'datetime': DateTimeHelper.datetime_to_string(
                                DateTimeHelper.timestamp_to_datetime_utc(candlestick['t'] // 1000)
                            ),
                        }
                        for candlestick in response.results
                    ]
                )

                start_date_ = end_date_
                end_date_ = min(end_date_ + dt.timedelta(days=days), to)

        return data

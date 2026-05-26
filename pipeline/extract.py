from tiingo import TiingoClient
from dotenv import load_dotenv
from datetime import timedelta
import datetime as dt
import os
import streamlit as st


load_dotenv()

class extract:
    def __init__(self, ticker, client, article_limit, end_date, start_date):
        self.ticker = ticker
        self.end_date = end_date
        self.start_date = start_date
        self.article_limit = article_limit
        self.client = client

    def extract_stock_data(self):
        try:
            stock_data = self.client.get_ticker_price(self.ticker,
                                                     frequency='daily',
                                                     startDate=self.start_date,
                                                     endDate=self.end_date)
        except Exception as e:
            raise RuntimeError(f"Data request failed for {self.ticker}") from e

        return stock_data

    def extract_news_data(self):
        try:
            news_data = self.client.get_news(tickers=[self.ticker],
                                             limit=self.article_limit,
                                             startDate=self.start_date,
                                             endDate=self.end_date)
        except Exception as e:
            raise RuntimeError(f"Data request failed for {self.ticker}") from e

        return news_data


def establish_tiingo_connection():
    '''
    This function configures a connection to the Tiingo API using
    the tiingo Python package.

    source: (Cameron Yick, https://pypi.org/project/tiingo/)
    '''
    tiingo_api_variable_name = "tiingo_api_token"
    try:
        api_token = os.getenv(tiingo_api_variable_name)
    except Exception as e:
        api_token = st.secrets[tiingo_api_variable_name]

    # Setup authorization dictionary
    config = {}
    config["session"] = True
    config["api_key"] = api_token

    # Initialise client
    client = TiingoClient(config)

    return client






import fastapi
from fastapi import FastAPI
import pandas as pd

app = FastAPI(
    title='Stock Price Prediction API',
    description='API to retrieve predictions and data about the META stock',
)

@app.get('/stock_data')
async def get_stock_data():
    stock_df = pd.read_csv('data/combined_output.csv')[['date',
                                                        'close',
                                                        'high',
                                                        'low',
                                                        'open',
                                                        'previous_day_close',
                                                        'volume']].rename(columns={'close': 'Close Price',
                                                                                   'high': 'Max Price',
                                                                                   'low': 'Min Price',
                                                                                   'open': 'Open Price',
                                                                                   'volume': 'Trading Volume',
                                                                                   'previous_day_close': 'Previous Day Close Price',
                                                                                   'date': 'Date'}).sort_index(ascending=False)
    return stock_df.to_json(orient='records')

@app.get('/news_data')
async def get_news_data():
    news_df = pd.read_csv('data/sentiment_counts.csv')[['date',
                                                        'positive_count',
                                                        'negative_count',
                                                        'neutral_count',
                                                        'total_articles']].rename(columns={'date': 'Date',
                                                                                           'positive_count': 'Positive Count',
                                                                                           'negative_count': 'Negative Count',
                                                                                           'neutral_count': 'Neutral Count',
                                                                                           'total_articles': 'Total Articles'})

    news_df['Month'] = news_df.apply(lambda x: x['Date'][0:7], axis=1)

    news_df = news_df.groupby(['Month']).agg({'Positive Count': sum,
                                              'Negative Count': sum,
                                              'Neutral Count': sum,
                                              'Total Articles': sum})

    news_df['Percent Positive'] = (news_df['Positive Count'] / news_df['Total Articles']) * 100
    news_df['Percent Negative'] = (news_df['Negative Count'] / news_df['Total Articles']) * 100
    news_df['Percent Neutral'] = (news_df['Neutral Count'] / news_df['Total Articles']) * 100

    news_df = news_df.drop(columns=['Positive Count',
                                    'Negative Count',
                                    'Neutral Count',
                                    'Total Articles']).reset_index()

    return news_df.to_json(orient='records')

import pandas as pd
import datetime
from main import get_previous_trading_day, main
from nn import run_nn


def get_stock_data():
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
                                                                                   'date': 'Date'}).sort_index(
        ascending=False)
    # Sort index sorts the data in date order most recent first
    return stock_df.to_json(orient='records')

def get_news_data():
    news_df = pd.read_csv('data/sentiment_counts.csv')[['date',
                                                        'positive_count',
                                                        'negative_count',
                                                        'neutral_count',
                                                        'total_articles']].rename(columns={'date': 'Date',
                                                                                           'positive_count': 'Positive Count',
                                                                                           'negative_count': 'Negative Count',
                                                                                           'neutral_count': 'Neutral Count',
                                                                                           'total_articles': 'Total Articles'})
    # Takes first 7 characters in the date column of each row and saves to new column Month
    news_df['Month'] = news_df.apply(lambda x: x['Date'][0:7], axis=1)

    # Aggregation of data
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

def run_pipeline():
    try:
        df = pd.read_csv('data/combined_output.csv')
        max_date = datetime.date.fromisoformat(df['date'].max())
        if max_date < get_previous_trading_day():
            main()
            updated_df = pd.read_csv('data/combined_output.csv')
            new_max_date = datetime.date.fromisoformat(updated_df['date'].max())
            return {"status": "success",
                    "triggered": True,
                    "message": "Pipeline completed successfully. Data updated",
                    "latest_date": str(new_max_date)}
        else:
            return {
                    "status": "success",
                    "triggered": False,
                    "message": "Data is already up to date.",
                    "latest_date": str(max_date)}
    except Exception as e:
        raise f"Failed to run pipeline: {e}"

def get_predictions_vs_actual():
    try:
        df = pd.read_csv('data/preds_vs_actual.csv')
        df = df.rename(columns={'date': 'Date',
                                'close': 'Close Price',
                                'predicted close': 'Predicted Close Price'})
        return df.to_json(orient='records')
    except Exception as e:
        raise f"Failed to retrieve predictions vs actual: {e}"

def get_predictions():
    try:
        data = run_nn()
        return data
    except Exception as e:
        raise f"Failed to retrieve predictions: {e}"

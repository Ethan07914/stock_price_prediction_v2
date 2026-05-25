# Please see (Commit 5961f05, ref: replaced pandas usage to polars for memory efficiency, https://github.com/Ethan07914/stock_price_prediction) for the changes made by claude code
# Prompt: "@index.py can you replace usage of pandas for polars utilising polars memory efficiency.
#          Can you also make a note of this prompt as a comment, your model details and the change you made in a brief comment."
# Model: claude-sonnet-4-6
# Change: Replaced all pandas (pd) usage with polars (pl) throughout. Migrated read_csv, rename,
#         select, groupby/agg, and sort calls to polars equivalents. Return values changed from
#         to_json(orient='records') strings to to_dicts() so FastAPI serialises proper JSON arrays.
#         Also fixed a pre-existing bug in /run_pipeline where new_max_date was computed from the
#         stale df instead of the freshly-read updated_df.

import fastapi
from fastapi import FastAPI, HTTPException, status
import polars as pl
import datetime
from main import get_previous_trading_day, get_next_trading_day, main
from nn import run_nn

app = FastAPI(
    title='Stock Price Prediction API',
    description='API to retrieve predictions and data about the META stock',
)

@app.get('/stock_data')
async def get_stock_data():
    stock_df = (
        pl.scan_csv('data/combined_output.csv')
        .select(['date', 'close', 'high', 'low', 'open', 'previous_day_close', 'volume'])
        .rename({'close': 'Close Price',
                 'high': 'Max Price',
                 'low': 'Min Price',
                 'open': 'Open Price',
                 'volume': 'Trading Volume',
                 'previous_day_close': 'Previous Day Close Price',
                 'date': 'Date'})
        .sort('Date', descending=True)
        .collect()
    )
    return stock_df.to_dicts()

@app.get('/news_data')
async def get_news_data():
    news_df = (
        pl.read_csv('data/sentiment_counts.csv')
        .select(['date', 'positive_count', 'negative_count', 'neutral_count', 'total_articles'])
        .rename({'date': 'Date',
                 'positive_count': 'Positive Count',
                 'negative_count': 'Negative Count',
                 'neutral_count': 'Neutral Count',
                 'total_articles': 'Total Articles'})
        .with_columns(pl.col('Date').str.slice(0, 7).alias('Month'))
        .group_by('Month')
        .agg([
            pl.col('Positive Count').sum(),
            pl.col('Negative Count').sum(),
            pl.col('Neutral Count').sum(),
            pl.col('Total Articles').sum(),
        ])
        .with_columns([
            (pl.col('Positive Count') / pl.col('Total Articles') * 100).alias('Percent Positive'),
            (pl.col('Negative Count') / pl.col('Total Articles') * 100).alias('Percent Negative'),
            (pl.col('Neutral Count') / pl.col('Total Articles') * 100).alias('Percent Neutral'),
        ])
        .drop(['Positive Count', 'Negative Count', 'Neutral Count', 'Total Articles'])
        .sort('Month')
    )
    return news_df.to_dicts()

@app.get('/run_pipeline')
async def run_pipeline():
    try:
        df = pl.read_csv('data/combined_output.csv')
        max_date = datetime.date.fromisoformat(df['date'].max())
        if max_date < get_previous_trading_day():
            main()
            updated_df = pl.read_csv('data/combined_output.csv')
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(e)}"
        )

@app.get('/predictions_vs_actual')
async def get_predictions_vs_actual():
    try:
        df = (
            pl.read_csv('data/preds_vs_actual.csv')
            .rename({'date': 'Date',
                     'close': 'Close Price',
                     'predicted close': 'Predicted Close Price'})
        )
        return df.to_dicts()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read data: {str(e)}"
        )

@app.get('/predictions')
async def get_predictions():
    try:
        data = run_nn()
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run the Neural Network: {str(e)}"
        )

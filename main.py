import os
import pandas as pd
from pipeline.extract import establish_tiingo_connection, extract
from pipeline.transform import transform
from pipeline.load import load
import datetime as dt
from ipynb.fs.defs.models.sentiment_model import run_text_classification, enrich_df, calculate_metrics

def run_extract_news(ticker, start_date, end_date, article_limit):
    print(
    '''
    STARTING ETL PIPELINE:
    
    EXTRACT
    ''')
    # EXTRACT
    # Initialised extract object
    extract_obj = extract(ticker, establish_tiingo_connection(), article_limit, end_date, start_date)

    # GEMINI 3 FAST
    # Prevents headers from being appended in the subsequent runs of the function
    file_path = 'data/extracted_news_data.csv'
    header_needed = not os.path.exists(file_path)

    extracted_news_df = pd.DataFrame(extract_obj.extract_news_data())

    extracted_news_df['tags'] = extracted_news_df['tags'].apply(tuple)
    extracted_news_df['tickers'] = extracted_news_df['tickers'].apply(tuple)

    extracted_news_df.to_csv('data/extracted_news_data.csv', index=False, mode='a', header=header_needed)

    return extracted_news_df

def run_extract_stock(ticker, start_date, end_date, article_limit):
    # EXTRACT
    # Initialised extract object
    extract_obj = extract(ticker, establish_tiingo_connection(), article_limit, end_date, start_date)

    extracted_stock_df = pd.DataFrame(extract_obj.extract_stock_data())
    extracted_stock_df.to_csv("data/extracted_stock_data.csv", index=False)

    return extracted_stock_df

def run_transform_stock():
    print('''
    TRANSFORM''')
    # TRANSFORM:
    # Initialise transform object
    transform_obj = transform(stock_data_file_path="data/extracted_stock_data.csv")


    transformed_stock_df = transform_obj.stock_df
    transformed_stock_df.to_csv('data/transformed_stock_data.csv', index=False)

    return transformed_stock_df

def run_transform_news():
    transform_obj = transform(news_data_file_path="data/extracted_news_data.csv")

    transformed_news_df = transform_obj.news_df
    transformed_news_df.to_csv("data/transformed_news_data.csv", index=False)

    print('''
        TEXT-CLASSIFICATION''')
    # TEXT-CLASSIFICATION:
    # Get Sentiment Classifications
    news_df_with_classifications = run_text_classification(transformed_news_df)

    # Enrich with additional columns
    enriched_news_df = enrich_df(news_df_with_classifications)
    enriched_news_df.to_csv("data/enriched_news_data.csv", index=False)

    # Calculate metrics & output as CSV
    news_df_with_metrics = calculate_metrics(enriched_news_df, True)
    news_df_with_metrics.to_csv('data/news_df_with_metrics.csv', index=False)

    return news_df_with_metrics



def run_load():
    print('''
    LOAD''')
    # LOAD:
    # Initialise load object
    load_obj = load('data/news_df_with_metrics.csv', 'data/transformed_stock_data.csv')
    load_obj.combined_df.to_csv('data/combined_output.csv', index=False, mode='a', header=None)

    df = pd.read_csv('data/combined_output.csv')
    deduplicated_df = df.drop_duplicates(keep='first', subset=['date'])
    deduplicated_df.to_csv('data/combined_output.csv', index=False)

    print('''
    END''')

    return load_obj.combined_df

def overwrite_files():
    files = ['news_df_with_metrics.csv', 'transformed_news_data.csv',
             'extracted_news_data.csv', 'extracted_stock_data.csv', 'transformed_stock_data.csv']
    prefix = 'data/'
    for file in files:
        if os.path.exists(prefix+file):
            os.remove(prefix+file)

def main():
    overwrite_files()
    ticker = ("META")
    article_limit = 1000
    df = pd.read_csv('data/combined_output.csv')
    start_date = df['date'].max()
    end_date = dt.date.today()

    run_extract_news(ticker, start_date, end_date, article_limit)
    run_extract_stock(ticker, start_date, end_date,  None)

    run_transform_stock()
    run_transform_news()

    run_load()


if __name__ == '__main__':
    main()
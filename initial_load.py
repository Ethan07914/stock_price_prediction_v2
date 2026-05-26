from main import overwrite_files, run_extract_stock, run_extract_news, run_transform_news, run_transform_stock, run_load
import datetime as dt
import pandas as pd

# Overwrite contents of certain files prevents duplicate news articles
overwrite_files()

# Initialise Boolean variable to be True
end_date_changed = True

end_date = dt.date.today()
start_date = dt.date.today() - dt.timedelta(days=1000)

article_limit = 1000
ticker = 'META'

# Retrieve news data first then stock data from same date range
run_extract_news(ticker, start_date, end_date, article_limit)


# Continue the loop until the data range stops changing, cannot go back further
while end_date_changed:
    prev_end_date = end_date
    current_extracted_df = pd.read_csv('data/extracted_news_data.csv')
    current_extracted_df['publishedDate'] = pd.to_datetime(current_extracted_df['publishedDate'], format='mixed').dt.date
    end_date = current_extracted_df['publishedDate'].min()
    start_date = end_date - dt.timedelta(days=1000)
    print(start_date, end_date)
    end_date_changed = True if prev_end_date != end_date else False
    # Keep fetching as much news data as possible
    run_extract_news(ticker, start_date, end_date, article_limit)

extracted_news_df = pd.read_csv('data/extracted_news_data.csv').drop_duplicates(keep='first')
extracted_news_df.to_csv('data/extracted_news_data.csv', index=False)
extracted_news_df['publishedDate'] = pd.to_datetime(extracted_news_df['publishedDate'], format='mixed').dt.date

start_date = pd.to_datetime(extracted_news_df['publishedDate']).dt.date.min()
end_date = pd.to_datetime(extracted_news_df['publishedDate']).dt.date.max()

run_extract_stock(ticker, start_date, end_date, article_limit)
run_transform_news()
run_transform_stock()
run_load()
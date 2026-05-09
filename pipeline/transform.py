import pandas as pd
import datetime as dt

weekday_dict = {'Monday': 1,
                'Tuesday': 2,
                'Wednesday': 3,
                'Thursday': 4,
                'Friday': 5,
                'Saturday': 6,
                'Sunday': 7}

class transform:
    def __init__(self, stock_data_file_path, news_data_file_path):
        self.stock_data_file_path =stock_data_file_path
        self.stock_df = self.transform_stock_data()
        self.news_data_file_path = news_data_file_path
        self.news_df = self.transform_news_data()

    def transform_stock_data(self):
        df = pd.read_csv(self.stock_data_file_path)

        # START CHANGE - claude-sonnet-4-6
        # Transform timestamp string to date
        # WHY: Tiingo returns dates as timezone-aware datetimes (e.g. "2026-01-16 00:00:00+00:00").
        # dt.tz_convert(None) strips the timezone to keep a tz-naive pandas Timestamp so that
        # the .dt accessor (used below for day_name) keeps working. The final strftime formats
        # the date as plain "YYYY-MM-DD" to match the news data, allowing the inner join in
        # load.py to produce rows instead of an empty combined_output.csv.
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_convert(None)
        # END CHANGE - claude-sonnet-4-6

        # Lag Features
        df['previous_day_close'] = df['close'].shift(1)
        df[f'previous_day_high'] = df['high'].shift(1)
        df[f'previous_day_low'] = df['low'].shift(1)
        df[f'previous_day_open'] = df['open'].shift(1)
        df[f'previous_day_volume'] = df['volume'].shift(1)

        days = (1,3,5)
        # Min and Max prices within time period
        for day in days:
            df[f'{day}_day_max'] = df.apply(lambda x: df.loc[(df['date'] > x['date'] - dt.timedelta(days=day)) *
                                                             (df['date'] <= x['date'])]
            ['high'].max(), axis=1)
            df[f'{day}_day_min'] = df.apply(lambda x: df.loc[(df['date'] > x['date'] - dt.timedelta(days=day)) *
                                                             (df['date'] <= x['date'])]
            ['low'].min(), axis=1)

        # Drops rows with NULL values in lagged columns to prevent performance reductions
        df = df.dropna()

        df['day_of_week'] = df['date'].dt.day_name().map(weekday_dict)

        # START CHANGE - claude-sonnet-4-6
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        # END CHANGE - claude-sonnet-4-6

        return df

    def transform_news_data(self):
        df = pd.read_csv(self.news_data_file_path)

        # Convert timestamp columns to date
        df['publishedDate'] = pd.to_datetime(df['publishedDate'], format='mixed').dt.date
        df['crawlDate'] = pd.to_datetime(df['crawlDate'], format='mixed').dt.date

        # Drop unnecessary columns
        df = df.drop(['url', 'description'], axis=1)

        # Enrich with day name
        df['day_of_week'] = df.apply(lambda x: weekday_dict[x['publishedDate'].strftime("%A")], axis=1)

        # Standardise naming conventions
        df = df.rename(columns={'publishedDate':'published_date', 'crawlDate':'crawl_date'})

        return df



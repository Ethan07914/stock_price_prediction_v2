import streamlit as st
import pandas as pd
import time

# DATAFRAMES
stock_df = pd.read_csv('data/combined_output.csv')[['date',
                                                           'close',
                                                           'high',
                                                           'low',
                                                           'open',
                                                           'previous_day_close',
                                                           'volume']]\
    .rename(columns={'close':'Close Price',
                     'high':'Max Price',
                     'low':'Min Price',
                     'open':'Open Price',
                     'volume':'Trading Volume',
                     'previous_day_close':'Previous Day Close Price',
                     'date':'Date'})\
    .sort_index(ascending=False)

news_df = pd.read_csv('data/enriched_news_data.csv')[['published_date',
                                                      'title',
                                                      'source',
                                                      'sentiment_label',
                                                      'sentiment_score',
                                                      'numerical_sentiment',
                                                      'is_positive',
                                                      'is_negative',
                                                      'is_neutral']]\
    .rename(columns={'published_date':'Date',
                     'title':'Title',
                     'source':'Source',
                     'sentiment_label':'Sentiment Label',
                     'sentiment_score':'Sentiment Score',
                     'numerical_sentiment':'Numerical Sentiment',
                     'is_positive':'Is Positive',
                     'is_negative':'Is Negative',
                     'is_neutral':'Is Neutral'})

news_df['Month'] = news_df.apply(lambda x: x['Date'][0:7], axis=1)

news_df = news_df.groupby(['Month']).agg({'Is Positive': sum,
                                          'Is Negative': sum,
                                          'Is Neutral': sum})

news_df['Percent Positive'] = (news_df['Is Positive'] / (news_df['Is Positive'] + news_df['Is Negative'] + news_df['Is Neutral'])) * 100
news_df['Percent Negative'] = (news_df['Is Negative'] / (news_df['Is Positive'] + news_df['Is Negative'] + news_df['Is Neutral'])) * 100
news_df['Percent Neutral'] = (news_df['Is Neutral'] / (news_df['Is Positive'] + news_df['Is Negative'] + news_df['Is Neutral'])) * 100
news_df = news_df.drop(columns=['Is Positive', 'Is Negative', 'Is Neutral'])

# VARIABLES
ticker = 'META'

# TITLE & HEADERS
st.title("Stock Price Prediction")
st.badge(ticker, color="blue", icon="♾️")

st.sidebar.header("Navigation")

st.subheader("Meta ($META) Daily Performance")
st.dataframe(stock_df.style.background_gradient(cmap="RdBu"), hide_index=True)

# BUTTONS
if st.button("Retrain"):
    st.balloons()
    pass




st.subheader("Close Price by Date")

st.line_chart(x='Date', y='Close Price',data=stock_df, color='#0668E1')

st.subheader("News Article Sentiment")
st.dataframe(news_df.style.background_gradient('Blues'))
st.subheader("Sentiment Percentages by Month")
st.bar_chart(news_df, color=['Green', 'Red', 'Orange'])

st.header("META Data Pipeline")

# GEMINI 3 FAST assisted in generation
# 1. Create a styled container for the 'terminal'
terminal_placeholder = st.empty()
terminal_text = "user@meta-pipeline:~$ starting process...\n"


def log_to_terminal(message):
    global terminal_text
    terminal_text += f"> {message}\n"
    # Wrap in st.code to get the terminal font and background
    terminal_placeholder.code(terminal_text, language="bash")


# --- Example Pipeline ---
if st.button("Run Pipeline"):
    log_to_terminal("Initializing extraction...")
    time.sleep(1)

    log_to_terminal("Extracting META stock data from API...")
    time.sleep(2)
    log_to_terminal("Extract Complete. [OK]")

    log_to_terminal("Running Transformations...")
    time.sleep(1)
    log_to_terminal("Transformation Complete. [OK]")

    log_to_terminal("Pipeline Finished Successfully.")

# End of co-generated code
import streamlit as st
import pandas as pd
import time

# 1.DATAFRAMES
stock_df = pd.read_csv('data/combined_output.csv')[['date',
                                                    'close',
                                                    'high',
                                                    'low',
                                                    'open',
                                                    'previous_day_close',
                                                    'volume']].rename(columns={'close':'Close Price',
                                                                                'high':'Max Price',
                                                                                'low':'Min Price',
                                                                                'open':'Open Price',
                                                                                'volume':'Trading Volume',
                                                                                'previous_day_close':'Previous Day Close Price',
                                                                                'date':'Date'}).sort_index(ascending=False)

news_df = pd.read_csv('data/sentiment_counts.csv')[['date',
                                                    'positive_count',
                                                    'negative_count',
                                                    'neutral_count',
                                                    'total_articles']].rename(columns={'date':'Date',
                                                                                       'positive_count':'Positive Count',
                                                                                       'negative_count':'Negative Count',
                                                                                       'neutral_count':'Neutral Count',
                                                                                       'total_articles':'Total Articles'})

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
                                'Total Articles'])


# 2.VARIABLES
ticker = 'META'


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
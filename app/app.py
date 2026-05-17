import streamlit as st
import pandas as pd
import time
import requests

URL = "http://127.0.0.1:8000"

# 1.DATAFRAMES
@st.cache_data(ttl=60)
def load_stock_data(URL):
    # Written with assistance of GEMINI 3, PROMPT: How do I call my API in my streamlit front end
    try:
        response = requests.get(URL+"/stock_data")
        if response.status_code == 200:
            data = response.json()
            return pd.read_json(data)
        else:
            st.error("Error fetching stock data")
            return None
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

@st.cache_data(ttl=60)
def load_news_data(URL):
    # Written with assistance of GEMINI 3, PROMPT: How do I call my API in my streamlit front end
    try:
        response = requests.get(URL+"/news_data")
        if response.status_code == 200:
            data = response.json()
            return pd.read_json(data)
        else:
            st.error("Error fetching news data")
            return None
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

stock_df = load_stock_data(URL)
news_df = load_news_data(URL)


# 2.VARIABLES
ticker = 'META'


st.title("Stock Price Prediction")
st.badge(ticker, color="blue", icon="♾️")

tab1, tab2 = st.tabs(['Analytics', 'Predictions'])

with tab1:
    st.subheader("Meta ($META) Daily Performance")
    st.dataframe(stock_df.style.background_gradient(cmap="RdBu"), hide_index=True)

    st.subheader("Close Price by Date")

    st.line_chart(x='Date', y='Close Price',data=stock_df, color='#0668E1')

    st.subheader("News Article Sentiment")
    st.dataframe(news_df.style.background_gradient('Blues'), hide_index=True)
    st.subheader("Sentiment Percentages by Month")
    st.bar_chart(news_df,
                 x="Month",
                 y=["Percent Positive", "Percent Negative", "Percent Neutral"],
                 color=['Green', 'Red', 'Orange'])



import streamlit as st
import pandas as pd
import time
import json
import requests
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api import (get_stock_data, get_news_data, get_predictions,
                                        get_predictions_vs_actual, run_pipeline)
import io



# 1.DATAFRAMES
@st.cache_data(ttl=60)
def load_stock_data():
    # Written with assistance of GEMINI 3, PROMPT: How do I call my API in my streamlit front end
    try:
        data = json.loads(get_stock_data())
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

@st.cache_data(ttl=60)
def load_news_data():
    # Written with assistance of GEMINI 3, PROMPT: How do I call my API in my streamlit front end
    try:
        data = json.loads(get_news_data())
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

@st.cache_data(ttl=60)
def trigger_pipeline():
    try:
        data = run_pipeline()
        return data
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

@st.cache_data(ttl=60)
def load_predicted_vs_actual_data():
    try:
        data = json.loads(get_predictions_vs_actual())
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

@st.cache_data(ttl=60)
def retrieve_predictions():
    try:
        data = get_predictions()
        return data
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

stock_df = load_stock_data()
news_df = load_news_data()


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

with tab2:
    with st.container(border=True):
        st.write("### Important Notice")
        st.write("- Predictions should not be used in isolation to guide decision making.")
        st.write("- The intention would be to run the predictions in the morning.")
        st.write("- The model predicts the close price of the stock the same day.")

    df = load_predicted_vs_actual_data()
    st.subheader("Predicted Close Price vs Actual Close Price")
    st.line_chart(x='Date', y=['Close Price', 'Predicted Close Price'], data=df)

    # Generated with assistance of GEMINI 3.1 FLASH
    # Initially second button would never cause the function to be executed
    if "pipeline_executed" not in st.session_state:
        st.session_state["pipeline_executed"] = False

    if st.button("Run Data Pipeline"):
        st.session_state["pipeline_executed"] = True
        data = trigger_pipeline()
        st.write(f'**{data["message"]}**')
        st.write(f'**Latest Date: {data["latest_date"]}**')

    if st.session_state['pipeline_executed']:
        if st.button("Predict"):
            prediction_data = retrieve_predictions()
            st.header(prediction_data['Next Trading Date'])
            st.metric("Predicted Close Price", round(prediction_data['Prediction'], 2))






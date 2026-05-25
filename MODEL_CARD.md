# PyTorch LSTM Stock Price Predictor

# Model details

## Text-Classification 

I used a Text-Classification model which was already fine-tuned to financial news data to classify the sentiment of related news articles which I then calculated percentages from by day.

- **Task**: Text Classification
- **Model**: ProsusAI/finbert
- **Link**: https://huggingface.co/ProsusAI/finbert
- **Alterations**: Base model

## Forecasting

I trained my own LSTM to predict stock prices from both stock market and related media data.

- **Task**: Forecasting
- **Model**: Custom PyTorch LSTM
- **Link**: https://docs.pytorch.org/docs/2.12/generated/torch.nn.LSTM.html
- **Alterations**: Full training 

# Intended use
- The model is for anyone interested in the stock market aware of the potential risks.
- It can be used to support trading decisions but should not be used in isolation without other reasoning.
- It should not be used if the user is not prepared to lose some of or all the money they invest.

# Data
- All data was retrieved from an API provided by Tiingo (https://www.tiingo.com/).
- Some news articles labelled by Tiingo as related to the META ticker did not seem to have a strong relation.
- Data went through a full ETL pipeline to transform it, news articles where passed through a sentiment classifier then metrics where calculated by day on those classifications before being passed into the LSTM.
- Data was split 70:30 for Training and Testing respectively,

# Metrics

- RMSE (root mean squared error) was used to assess the accuracy of my model.
- RMSE is useful for stock price prediction as it emphasises when the model predicted significantly wrong.
- Takes the root of the average of the squared differences between predicted and actual.
- Due to the squaring of the differences before the average large errors are highlighted.

# Limitations & failure cases

- Not all articles retrieved by the API seem to be related to the META stock.
- The model seems to pick up on trends late.
- The model can both under or over-estimate swings in the market.

# Ethics & risks

- The model predicting the close price of the META stock significantly wrong could contribute to a loss of money for a user.

## Mitigations

- All users should be aware not to use the model in isolation for decision-making.

## Deployment Notes

- Models will be runnable on most desktops and laptops without the need for using virtual machines.
- Front-end deployed on Streamlit Community Cloud https://stockpriceprediction-77xj5kzyytrrfjc9byuefu.streamlit.app/

# References

- (Sarah Lee, NumberAnalytics.com, Understanding RMSE Use in Forecasting Models for Accurate Decision Making, 2025, https://www.numberanalytics.com/blog/understanding-rmse-use-in-forecasting-models-accurate-decision-making)

from ipynb.fs.defs.models.neural_network import (get_device, create_features, remove_nulls, scale_data,
                                                 split_data, convert_to_tensors, StockDataset, create_datasets,
                                                 create_dataloaders, Net, run_training_loop, test_model,
                                                 get_rmse)
import pandas as pd
import torch
from main import get_next_trading_day



# Built as a dict rather than renaming CSV columns because combined_output.csv already contains
# pre-computed previous_day_close/high/low/open/volume columns. Renaming the current-day columns
# (close → previous_day_close, etc.) produced duplicate column names, causing sklearn's scaler to
# raise a feature-order mismatch. Building from source columns directly avoids that ambiguity and
# guarantees the exact column order the scaler was fitted on. — claude-sonnet-4-6
def get_data_for_prediction():
    next_trading_day = get_next_trading_day()
    day_of_week = next_trading_day.weekday() + 1
    last_row = pd.read_csv('data/combined_output.csv').iloc[-1]
    return pd.DataFrame([{
        'previous_day_close': last_row['close'],
        'previous_day_high': last_row['high'],
        'previous_day_low': last_row['low'],
        'previous_day_open': last_row['open'],
        'previous_day_volume': last_row['volume'],
        'day_of_week': day_of_week,
        'previous_day_numerical_sentiment': last_row['numerical_sentiment'],
        'previous_day_mean_sentiment_probability': last_row['mean_sentiment_probability'],
        'previous_day_percent_positive': last_row['percent_positive'],
        'previous_day_percent_negative': last_row['percent_negative'],
        'previous_day_percent_neutral': last_row['percent_neutral'],
    }], index=[next_trading_day]), next_trading_day

def run_nn():
    df = pd.read_csv('data/combined_output.csv')
    df = create_features(df)
    df = remove_nulls(df, True)

    device = get_device()

    X_train_df_as_numpy, X_test_df_as_numpy, Y_train_df_as_numpy, Y_test_df_as_numpy, scalar_x, scalar_y = scale_data(df, 1)
    X_train, X_test, Y_train, Y_test = split_data(X_train_df_as_numpy, X_test_df_as_numpy, Y_train_df_as_numpy,
                                                  Y_test_df_as_numpy)
    X_train, X_test, Y_train, Y_test = convert_to_tensors(X_train, X_test, Y_train, Y_test)
    train_dataset, test_dataset = create_datasets(X_train, X_test, Y_train, Y_test)
    train_dataloader, test_dataloader = create_dataloaders(train_dataset, test_dataset, 4)

    model = Net(1, 32, 4, 1, device)
    model.to(device)

    output = run_training_loop(1e-3, 500, model, X_train, Y_train)

    train_output_prediction, train_actual, test_output_prediction, test_actual = test_model(scalar_y, Y_train, X_test, Y_test, model, output)

    new_data, next_trading_day = get_data_for_prediction()
    new_data_scaled = scalar_x.transform(new_data).reshape((-1, 11, 1))
    new_tensor = torch.tensor(new_data_scaled).float()
    pred = model(new_tensor)
    pred_value = scalar_y.inverse_transform(pred.detach().cpu().numpy())


    train_rmse, test_rmse = get_rmse(train_actual, train_output_prediction, test_actual, test_output_prediction)

    return {"Train RMSE": train_rmse,
            'Prediction': float(pred_value[0][0]),
            'Next Trading Date': str(next_trading_day)}


if __name__ == "__main__":
    print(run_nn())

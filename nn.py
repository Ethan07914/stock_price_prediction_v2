from ipynb.fs.defs.models.neural_network import (get_device, create_features, remove_nulls, scale_data,
                                                 split_data, convert_to_tensors, StockDataset, create_datasets,
                                                 create_dataloaders, Net, run_training_loop, test_model,
                                                 get_rmse)
import pandas as pd

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

    train_rmse, test_rmse = get_rmse(train_actual, train_output_prediction, test_actual, test_output_prediction)

    return {"Train RMSE": train_rmse}


if __name__ == "__main__":
    run_nn()

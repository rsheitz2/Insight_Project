from sklearn.metrics import mean_squared_error
import numpy as np
from helperfunctions import is_high_bp
import pandas as pd

def prophet_model(d_input, shift, which_bp, patient_id):
    X, y = d_input['X'], d_input['Y']
    ynow, time_now = d_input['bp'], d_input['now']

    forecast = pd.read_csv('/Users/robertheitz/Documents/DataSci/Insight/Insight_Project/Insight_Project_Framework/Forecasts/{}_patient{}.csv'.format(which_bp, patient_id))

    ypred_now = forecast['yhat'].iloc[-10]
    yhat = forecast['yhat'].iloc[:-10].values
    rmse = (forecast['yhat_upper'] - forecast['yhat_lower']).iloc[:-10].mean()
    rmse = rmse/2.0
    high_bp = is_high_bp(ynow, ypred_now, shift, rmse)

    x_max_values, y_max_values = [], []
    high_x, high_y,  = [], []
    for x_true, y_true, y_pred in zip(X, y, yhat):
        if is_high_bp(y_true, y_pred, shift, rmse):
            high_x.append(x_true)
            high_y.append(y_true)
        x_max_values.append(x_true)
        y_max_values.append(y_pred+shift+rmse)

    d_output = {'high_bp': high_bp, 'high_x': high_x, 'high_y': high_y,
                'x_max_values': x_max_values, 'y_max_values': y_max_values,
                'forecast': ypred_now, 'rmse': rmse}

    return d_output
    

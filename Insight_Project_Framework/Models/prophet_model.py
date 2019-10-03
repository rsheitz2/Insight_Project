import pickle
from fbprophet import Prophet
from sklearn.metrics import mean_squared_error
import numpy as np
from helperfunctions import is_high_bp

def prophet_model(d_input, shift, which_bp, patient_id):
    m = pickle.load(open('/Users/robertheitz/Documents/DataSci/Insight/DuringInsight/DevSetup/FlaskSetup/MyStarterApp/PatientData/Sav/{}_patient{}.sav'.format(which_bp, patient_id), 'rb'))
    X, y = d_input['X'], d_input['Y']
    ynow, time_now = d_input['bp'], d_input['now']

    future = m.make_future_dataframe(periods=1, freq='D')
    forecast = m.predict(future)

    ypred_now = forecast['yhat'].iloc[-1]
    yhat = forecast['yhat'].iloc[:-1].values
    rmse = (forecast['yhat_upper'] - forecast['yhat_lower']).iloc[:-1].mean()
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
                'x_max_values': x_max_values, 'y_max_values': y_max_values}

    return d_output
    

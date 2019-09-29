from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

def high_pressure_cal(sys_pressure, dia_pressure, heart_rate):
    if (float(sys_pressure) > 160):
        return True

    return False

def is_high_bp(y, y_pred, shift, rmse):
    if y > y_pred + shift + rmse:
        return True
    return False

def lin_model(X, y, ynow, time_now, shift):
    lin_model = LinearRegression()

    lin_model.fit(X, y)
    ypred_now = lin_model.predict(np.array(time_now).reshape(1, 1))
    ypred_now = ypred_now.squeeze()

    yhat = lin_model.predict(X)
    yhat = yhat.reshape(-1, 1)
    rmse = np.sqrt(mean_squared_error(y, yhat))
    
    b = lin_model.intercept_
    m = lin_model.coef_

    high_bp = is_high_bp(ynow, ypred_now, shift, rmse)

    high_x, high_y,  = [], []
    for x_true, y_true, y_pred in zip(X, y, yhat):
        if is_high_bp(y_true, y_pred, shift, rmse):
            high_x.append(x_true)
            high_y.append(y_true)

    return high_bp, high_x, high_y

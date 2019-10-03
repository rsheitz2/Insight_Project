from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np
from helperfunctions import is_high_bp


def lin_model(d_input, shift):
    X, y = d_input['X'], d_input['Y']
    ynow, time_now = d_input['bp'], d_input['now']
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

    x_min, x_max = X.min(), X.max()
    y_min, y_max = m*x_min + b + 20, m*x_max + b + 20
    y_min, y_max = y_min.squeeze(), y_max.squeeze()
    x_max_values, y_max_values = [x_min, x_max], [y_min, y_max]

    d_output = {'high_bp': high_bp, 'high_x': high_x, 'high_y': high_y,
                'x_max_values': x_max_values, 'y_max_values': y_max_values}

    return d_output

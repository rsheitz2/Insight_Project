import pandas as pd
from datetime import timedelta

def high_pressure_cal(sys_pressure, dia_pressure, heart_rate):
    if (float(sys_pressure) > 160):
        return True

    return False

def is_high_bp(y, y_pred, shift, rmse):
    if y > y_pred + shift + rmse:
        return True
    return False

def Num_To_Time(num):
    num = num/2
    num // 1
    time_date = pd.to_datetime(num, unit='D')
    time_date = time_date + timedelta(days=17314)

    return time_date

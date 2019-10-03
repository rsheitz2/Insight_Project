def high_pressure_cal(sys_pressure, dia_pressure, heart_rate):
    if (float(sys_pressure) > 160):
        return True

    return False

def is_high_bp(y, y_pred, shift, rmse):
    if y > y_pred + shift + rmse:
        return True
    return False

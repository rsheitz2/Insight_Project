from flaskapp import app
from flask import Flask, Markup, render_template, request, send_file, redirect
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import matplotlib
from linear_model import lin_model
from prophet_model import prophet_model
import mpld3
from mpld3 import plugins
import numpy as np
from datetime import timedelta 

# Not sure what this does but fixes NSView.m Assertion failed error
matplotlib.use('Agg')


def Num_To_Time(num):
    num = num/2
    num // 1
    time_date = pd.to_datetime(num, unit='D')
    time_date = time_date + timedelta(days=17314)

    return time_date

def Make_Plot(d_input, d_model, y_label, total=False):
    X, Y = d_input['X'], d_input['Y']
    bp, time_now = d_input['bp'], d_input['now']
    x_high, y_high = d_model['high_x'], d_model['high_y']
    x_max_values, y_max_values = d_model['x_max_values'],d_model['y_max_values']

    #X_date = pd.to_datetime(X.squeeze(), unit='D')


    
    figsize=(3, 4)
    if total:
        figsize=(6, 4)
        
    #fig, ax = plt.subplots(figsize=figsize)
    #fig, ax = plt.subplots()
    linewidth, markersize = 0.2, 12

    fig, ax = plt.subplots(figsize=figsize)
    
    plt.suptitle('Your past blood pressures', fontsize=16)
    plt.plot(time_now, bp, 'co', label='todays recording', markersize=markersize)
    plt.plot(time_now, bp, 'ko')
    plt.plot(time_now, bp, 'k+', markersize=2*markersize)

    if total:
        plt.plot(X, Y, 'o--', linewidth=linewidth, label='past recordings')
        if len(x_high) > 0:
            plt.plot(x_high, y_high, 'ro', label='high pressures')
        plt.plot(x_max_values, y_max_values, 'ro')
    
    #ax.plot([X.min(), time_now], [bp, bp], 'c--', linewidth=4)
    
    plt.xlabel('time (days)', fontsize=18)
    plt.ylabel(y_label)

    my_xticks, x_vals = [], []
    time_now_date = Num_To_Time(time_now)
    if total:
        time_min, time_mid = X.min(), X.mean()
        time_min_date = Num_To_Time(time_min)
        time_mid_date = Num_To_Time(time_mid)
        
        my_xticks.append(time_min_date.strftime("%Y/%m/%d"))
        my_xticks.append(time_mid_date.strftime("%Y/%m/%d"))
        my_xticks.append(time_now_date.strftime("%Y/%m/%d"))

        x_vals.append(time_min)
        x_vals.append(time_mid)
        x_vals.append(time_now)
    else:
        my_xticks.append(time_now_date.strftime("%Y/%m/%d"))
        x_vals.append(time_now)
    
    plt.xticks(x_vals, my_xticks)
    #if x_zoomed:
    #    ax.set_xlim([time_now - 10, time_now + 10])
    plt.legend()

    return mpld3.fig_to_html(fig)


@app.route('/', methods=['GET', 'POST'])
@app.route('/input')
def user_input():

    return render_template('input.html')
    

@app.route('/output')
def user_results():
    
    # Get values from form
    patient_id = request.args.get('patient_id')
    sys_bp = request.args.get('sys_bp')
    dia_bp = request.args.get('dia_bp')
    
    try:
        patient_id = int(patient_id)
        sys_bp = float(sys_bp)
        dia_bp = float(dia_bp)
    except ValueError:
        print ('Invalid user id or blood pressure, fix later')
        return redirect('/input')
    except TypeError:
        pass

    df = pd.read_csv('/Users/robertheitz/Documents/DataSci/Insight/DuringInsight/DevSetup/FlaskSetup/MyStarterApp/PatientData/patients_all.csv')

    patient_id = np.sort(df['patient'].unique())[patient_id - 1]
    df_patient = df[df['patient'] == patient_id][['systolic', 'diastolic', 'index_time']]
    df_patient = df_patient.groupby('index_time').mean().reset_index()
    
    Y_sys = df_patient['systolic'].values
    Y_dia = df_patient['diastolic'].values
    X = df_patient['index_time'].values
    X = 2*X
    
    Y_sys = Y_sys.reshape(-1, 1)
    Y_dia = Y_dia.reshape(-1, 1)
    X = X.reshape(-1, 1)

    time_now = X.max() + 2

    d_sys_input = {'X': X, 'Y': Y_sys, 'bp': sys_bp, 'now': time_now}
    d_dia_input = {'X': X, 'Y': Y_dia, 'bp': dia_bp, 'now': time_now}
    d_sys_model = prophet_model(d_sys_input, 20, 'systolic', patient_id)
    d_dia_model = prophet_model(d_dia_input, 10, 'diastolic', patient_id)
    
    high_bp = False
    if d_sys_model['high_bp'] or d_dia_model['high_bp']:
        high_bp = True
    
    bp_img_sys = Make_Plot(d_sys_input, d_sys_model, 'systolic')
    bp_tot_img_sys = Make_Plot(d_sys_input, d_sys_model, 'systolic', True)
    bp_img_dia = Make_Plot(d_dia_input, d_dia_model, 'diastolic')
    bp_tot_img_dia = Make_Plot(d_dia_input, d_dia_model, 'diatolic', True)
    
    return render_template('output.html',
                           bp_img_sys=bp_img_sys, bp_tot_img_sys=bp_tot_img_sys,
                           bp_img_dia=bp_img_dia, bp_tot_img_dia=bp_tot_img_dia,
                           patient_id=patient_id, sys_bp=sys_bp, dia_bp=dia_bp,
                           high_bp=high_bp)

@app.route('/restart')
def back_to_input():

    return redirect('/input') 


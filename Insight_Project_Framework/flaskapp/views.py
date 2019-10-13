from flaskapp import app
from flask import Flask, Markup, render_template, request, send_file, redirect
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from mpld3 import plugins, fig_to_html
import numpy as np
import os
from helperfunctions import Num_To_Time
from prophet_model import prophet_model

matplotlib.use('Agg')

def Make_Plot(d_input, d_model, y_label, total=False):
    X, Y = d_input['X'], d_input['Y']
    bp, time_now = d_input['bp'], d_input['now']
    x_high, y_high = d_model['high_x'], d_model['high_y']
    x_max_values, y_max_values = d_model['x_max_values'],d_model['y_max_values']
    yhat, rmse = d_model['forecast'], d_model['rmse']

    w, h = plt.figaspect(1.4)
    if total:
        w, h = plt.figaspect(0.8)
        
    linewidth, markersize = 0.2, 12
    fig, ax = plt.subplots(figsize=(w, h))
    
    plt.suptitle('Your past blood pressures', fontsize=16)
    plt.plot(time_now, bp, 'co', markersize=markersize)
    plt.plot(time_now, bp, 'ko', label='today '+y_label)
    plt.plot(time_now, bp, 'k+', markersize=2*markersize)

    if total:
        plt.plot(X, Y, 'o', linewidth=linewidth, label='past recordings')
        if len(x_high) > 0:
            plt.plot(x_high, y_high, 'ro', label='high pressures')
        plt.plot(x_max_values, y_max_values, 'r--')
        
    else:
        plt.plot([time_now+1, time_now+3], [yhat, yhat], 'b', linewidth=6,
                 label='forecast')
        plt.plot([time_now+1.25, time_now+2.75], [yhat+rmse, yhat+rmse], 'c',
                 label='upper 68% confidence', linewidth=6)
        if y_label == 'systolic':
            plt.plot([time_now+1.5, time_now+2.5], [yhat+rmse+20, yhat+rmse+20], 'r',
                     label='anomaly', linewidth=6)
            plt.plot([time_now+2, time_now+2], [yhat, yhat+rmse+20], 'k--')
        else:
            plt.plot([time_now+1.5, time_now+2.5], [yhat+rmse+10, yhat+rmse+10], 'r',
                     label='anomaly', linewidth=6)
            plt.plot([time_now+2, time_now+2], [yhat, yhat+rmse+10], 'k--')

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

        plt.ylabel(y_label, fontsize=20, labelpad=-5)
    else:
        my_xticks.append(time_now_date.strftime("%Y/%m/%d"))
        x_vals.append(time_now)
        plt.xlim(time_now-2, time_now+5)
        
    plt.xticks(x_vals, my_xticks)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend()

    return fig_to_html(fig)


@app.route('/', methods=['GET', 'POST'])
@app.route('/input')
def user_input():

    return render_template('input.html')
    

@app.route('/output')
def user_results():
    
    patient_id = request.args.get('patient_id')
    sys_bp = request.args.get('sys_bp')
    dia_bp = request.args.get('dia_bp')

    try:
        patient_id = int(patient_id)
        sys_bp = float(sys_bp)
        dia_bp = float(dia_bp)
    except ValueError:
        return render_template('id_error.html')

    possible_ids = [8,13,15,18,19,20,23,26,27,29,40,44,46,47,48,50,53,55,57,60,
                    63,64,68,79,81,82,93,94,145,148,150,151,155,162,163,164,165,
                    166,167,172,173,174,178,179,180,186,198,199,203,210,211,213,
                    214,215,217,220,222,225,229,230,231,232,233,235,236,237,240,
                    241,242,243,245,246,249,252,255,258,259,264,265,268,269,270,
                    271,272,273,274,276,277,278,279,282,283,294,298,299,301,302,
                    303,305,309,310,317,319,321,322,323,329,330,332,333,335,337,
                    341,342,345,347,349,350,352,354,356,357,358,359,360,361,362,
                    364,365,366,368,369,371,372]

    if (patient_id > len(possible_ids)) or (patient_id < 1):
        return render_template('id_unknown.html')

    cwd = os.getcwd()
    df_patient = pd.read_csv('{}/../Data/Patients/patient{}.csv'.format(cwd, possible_ids[patient_id-1]))
    
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
    d_sys_model = prophet_model(d_sys_input, 20, 'systolic', possible_ids[patient_id-1])
    d_dia_model = prophet_model(d_dia_input, 10, 'diastolic', possible_ids[patient_id-1])
    
    high_bp = False
    if d_sys_model['high_bp'] or d_dia_model['high_bp']:
        high_bp = True
    
    bp_img_sys = Make_Plot(d_sys_input, d_sys_model, 'systolic')
    bp_tot_img_sys = Make_Plot(d_sys_input, d_sys_model, 'systolic', True)
    bp_img_dia = Make_Plot(d_dia_input, d_dia_model, 'diastolic')
    bp_tot_img_dia = Make_Plot(d_dia_input, d_dia_model, 'diastolic', True)
    
    return render_template('output.html',
                           bp_img_sys=bp_img_sys, bp_tot_img_sys=bp_tot_img_sys,
                           bp_img_dia=bp_img_dia, bp_tot_img_dia=bp_tot_img_dia,
                           patient_id=patient_id, sys_bp=sys_bp, dia_bp=dia_bp,
                           high_bp=high_bp)

@app.route('/restart')
def back_to_input():

    return redirect('/input')

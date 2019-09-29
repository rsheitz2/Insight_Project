from flaskapp import app
from flask import Flask, Markup, render_template, request, send_file, redirect
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import matplotlib
from linear_model import lin_model

# Not sure what this does but fixes NSView.m Assertion failed error
matplotlib.use('Agg')

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
        
    df = pd.read_csv('/Users/robertheitz/Documents/DataSci/Insight/Project/DevSetup/FlaskSetup/MyStarterApp/PatientData/patients.csv')
    #time_now = df['index_time'].max() + 0.5
    
    df_patient = df[df['patient'] == patient_id][['systolic', 'diastolic', 'index_time']]
    
    Y_sys = df_patient['systolic'].values
    Y_dia = df_patient['diastolic'].values
    X = df_patient['index_time'].values
    
    Y_sys = Y_sys.reshape(-1, 1)
    Y_dia = Y_dia.reshape(-1, 1)
    X = X.reshape(-1, 1)

    time_now = 844.0
    xmin, xmax = df_patient['index_time'].min(), time_now-0.5

    high_bp = False
    high_bp_sys, x_high_sys, y_high_sys = lin_model(X, Y_sys, sys_bp, time_now, 20)
    high_bp_dia, x_high_dia, y_high_dia = lin_model(X, Y_dia, dia_bp, time_now, 10)
    if high_bp_sys or high_bp_dia:
        high_bp = True
        
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))
    linewidth, markersize = 0.2, 12

    fig.suptitle('Your past blood pressures', fontsize=16)
    ax1.plot(X, Y_sys, 'o--', linewidth=linewidth, label='past recordings')
    if len(x_high_sys) > 0:
        ax1.plot(x_high_sys, y_high_sys, 'ro', label='high pressures')
    ax1.plot(time_now, sys_bp, 'k+', markersize=markersize)
    ax1.plot(time_now, sys_bp, 'ko', label='todays recording')
    ax1.set_xlabel('time (days)')
    ax1.set_ylabel('systolic blood pressure')
    ax1.legend()
    
    ax2.plot(X, Y_dia, 'o--', linewidth=linewidth, label='past recordings')
    ax2.plot(time_now, dia_bp, 'k+', markersize=markersize)
    ax2.plot(time_now, dia_bp, 'ko', label='todays recording')
    if len(x_high_dia) > 0:
        ax2.plot(x_high_dia, y_high_dia, 'ro', label='high pressures')
    ax2.set_xlabel('time (days)')
    ax2.set_ylabel('diastolic blood pressure')
    ax2.legend()
    
    bp_img = BytesIO()
    plt.savefig(bp_img, format='png')
    bp_img.seek(0)
        
    bp_image = base64.b64encode(bp_img.read()).decode('utf-8')
    
    # Send lists and image to html file
    return render_template('output.html', bp_image=bp_image,
                           patient_id=patient_id, sys_bp=sys_bp, dia_bp=dia_bp,
                           high_bp=high_bp)

@app.route('/restart')
def back_to_input():

    return redirect('/input') 


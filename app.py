from threading import Timer
from pathlib import Path
import webbrowser
import subprocess
import json
import sys
import os
from flask import Flask, flash, request, send_from_directory, url_for, render_template, redirect, jsonify,make_response
from werkzeug.utils import secure_filename


import sqlite3
from flask import g

import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

import analytics

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv','tsv'}
DATABASE = 'C:\\3Projects\\marketing material\\dtkube\\Rivu\\poc\\database.db'

# set the project root directory as the static folder, you can set others.
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder,
                static_folder=static_folder)
else:
    app = Flask(__name__)

app.config['SECRET_KEY'] = 'the random string'    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ~~~ Helper functions
@app.before_first_request
def init_app():
    cur = get_db().cursor()
    cur.execute("CREATE  TABLE IF NOT EXISTS data_assessment(ID INTEGER PRIMARY KEY AUTOINCREMENT, name text, description text, filename text ) ")
    cur.execute("CREATE  TABLE IF NOT EXISTS data_assessment_column(name TEXT,data_assessment_id INTEGER,FOREIGN KEY(data_assessment_id) REFERENCES data_assessment (id)) ")
   
    cur.close()
#~~~ Routes
   
@app.route("/")
def main():
    return render_template('index.html',context ={})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/main_menu/<menu>/<submenu>",methods=['GET','POST'])
def menu(menu,submenu):
    cur = get_db().cursor()
    context = {}
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
          # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Save the record            
            cur.execute(f"insert into data_assessment(name,description,filename) values('{name}','{description}', '{filename}')")
            data_assessment_id = cur.lastrowid
            # Get columns
            columns = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename)).columns
            for col in columns:
                cur.execute(f"insert into data_assessment_column(data_assessment_id,name) values({data_assessment_id},'{col}')")
                     
            get_db().commit()
    context['menu'] = menu
    context['submenu'] = submenu

    data_assessment = cur.execute('select * from data_assessment').fetchall()
    data_assessment_res = []
    for data in data_assessment:
        columns = cur.execute(f'select name from data_assessment_column where data_assessment_id = {data[0]}').fetchall()
        # setattr(data, 'columns', columns)
        cols = []
        for c in columns:
            cols.append(c[0])
        data_assessment_res.append({"data": data, "column": cols})
    if menu == 'data_assessment':
        action = request.args.get('action',type=str)
        context['data_assessment'] = data_assessment_res
        filename = request.args.get('filename',type=str)
        if submenu == 'bias':            
            if action == 'assess':                
                target = request.args.get('target',type=str)
                context['bias'] = bias(filename,target)
            
        elif submenu == 'quality':    
            if action == 'quality':
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                context['quality'] = quality(filename)

    return render_template(f'/{menu}/{submenu}.html',context = context)

# @app.route("/histo/<file_path>/<file_name>/<target>")
def bias(filename,target):
    # buffer = analytics.histo()
    # response = make_response(buffer.getvalue())
    # response.mimetype = 'image/png'
    # return make_response(response)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv (filepath)
    res = analytics.bias_detection(df,target)
    # response = make_response(res)
    # response.mimetype = 'plain/text'
    return res

def quality(filename):
    # buffer = analytics.histo()
    # response = make_response(buffer.getvalue())
    # response.mimetype = 'image/png'
    # return make_response(response)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv (filepath)
    res = analytics.missing_values_detection(df)
    print("=============================")
    print(res)
    # response = make_response(res)
    # response.mimetype = 'plain/text'
    return res

# ~~~ The main function
if __name__ == "__main__":
    app.run(debug=True)

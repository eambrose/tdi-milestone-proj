from flask import Flask, render_template, request, redirect, session
import requests
import os
import simplejson as json
from bokeh.embed import components
from bokeh.plotting import figure, show, output_notebook
from bokeh.resources import CDN
import datetime as dt
import pandas as pd
import numpy as np

app = Flask(__name__)
api_key = os.environ.get('QUANDL_API_KEY')

@app.route('/')
def main():
  return redirect('/index')

app.vars={} #added by Ellen
@app.route('/index', methods=['GET','POST'])
def index():
  if request.method == 'GET':
    return render_template('index.html')
  else:
    app.vars['stock'] = request.form['stockID'] 
    stockID = app.vars['stock']
    return redirect('/graph/'+stockID)

@app.route('/graph/<userstock>',methods=['GET','POST'])
def graph(userstock):
    r = requests.get("https://www.quandl.com/api/v3/datasets/WIKI/{}.json?api_key={}".format(userstock,api_key))
    c = r.content
    j = json.loads(c)
    raw_data = j['dataset']['data']
    dates = [raw_data[x][0] for x in range(len(raw_data))]
    def make_date(date_str):
        y,m,d = date_str.split('-')
        return dt.date(year = int(y), month = int(m), day = int(d))
    new_dates = map(make_date, dates)
    dates_new = pd.DatetimeIndex(new_dates[0:30])
    close = [raw_data[x][4] for x in range(len(raw_data))]
    close_new = pd.Series(close[0:30])
    close_new.index = dates_new
    p = figure(x_axis_type='datetime', plot_width=600, plot_height=400)
    p.line(close_new.index, close_new, line_width=3)
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price (USD)'
    p.title = 'Closing price from QUANDL WIKI - ' + userstock
    script,div = components(p,CDN)
    return render_template('graph.html',stockID=userstock, rthing='',script=script, div=div)

if __name__ == '__main__':
  app.run(host='0.0.0.0')

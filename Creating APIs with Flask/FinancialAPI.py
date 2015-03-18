#-------------------------------------------------------------------------------
# Name:        FinancialAPI
# Purpose:     Creating a financial API using Flasks and pulling data
#              from Yahoo finance.
# Author:      Andrew Mellor
#
# Created:     18/03/15
# Copyright:   (c) Andrew Mellor 2015
# Licence:     The MIT License (MIT)
#-------------------------------------------------------------------------------

import requests as rq
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from networkx.readwrite import json_graph
import json
from flask import Flask, request, send_file, url_for

app = Flask(__name__)

API_BASE = "https://query.yahooapis.com/v1/public/yql"
API_ENV = "store://datatables.org/alltableswithkeys"
API_FORMAT = "json"
API_CALLBACK = ""

@app.route("/")
def hello():
    return "Server Operational"

@app.route('/company/<companyName>')
def show_company_prices(companyName):
    # 
    # Example URL : http://localhost:5000/company/AAPL?startDate=2015-01-01&endDate=2015-01-10
    startDate =  request.args.get('startDate')
    endDate =  request.args.get('endDate')
    #print "Start Date is {}, End Date is {}".format(startDate, endDate)    
    query = 'select * from yahoo.finance.historicaldata where symbol in ("{}") and startDate = "{}" and endDate = "{}"'.format(companyName,startDate,endDate)
    payload = {'q':query,
               'env':API_ENV,
               'format':API_FORMAT,
               'callback': API_CALLBACK}               
    data = rq.get(API_BASE, params=payload)
    return data.text

@app.route('/network')
def covariance_matrix():
    now = datetime.now()
    endDate = now - timedelta(days=1)
    endDate = endDate.strftime("%Y-%m-%d")    
    startDate = now - timedelta(days=7)
    startDate = startDate.strftime("%Y-%m-%d")
    companies = ["BABA","AMZN","MSFT","YHOO", "GOOG","IBM",#"DELL",
                 "FB", "MER", "GS", "C", "JPM"]
    data = np.zeros(shape=(len(companies), 7-2), dtype=float)
    i = 0
    for company in companies:    
        query = 'select * from yahoo.finance.historicaldata where symbol in ("{}") and startDate = "{}" and endDate = "{}"'.format(company,startDate,endDate)
        payload = {'q':query,
               'env':API_ENV,
               'format':API_FORMAT,
               'callback': API_CALLBACK}               
        response = rq.get(API_BASE, params=payload).json()
            
        try:
            for ix,entry in enumerate(response['query']['results']['quote']):
                data[i,ix] = entry['Close']
            i+=1
        except:
            print response
    
    correlation = np.corrcoef(data)
    correlation = np.where(abs(correlation)<0.75,0,correlation)
    G = nx.Graph(correlation)
    nx.set_node_attributes(G,'company',{ix:company for ix,company in enumerate(companies)})
    
    if request.args.get('data')=='True':
        jsonNetwork = json_graph.node_link_data(G)
        return json.dumps(jsonNetwork)
    else:
        fig = plt.figure(figsize=[10,10])
        nx.draw_networkx(G, 
                         width=[2*abs(x[2]['weight']) for x in G.edges(data=1)],
                         edge_color=[1-2*(x[2]['weight']<0) for x in G.edges(data=1)],
                         labels=nx.get_node_attributes(G,'company'), 
                         font_weight='bold')
        plt.axis('off')
        fig.savefig('./correlation.png',bbox_inches="tight")    
        return send_file('correlation.png', mimetype='image/png')

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

#url_for('static', filename='basic_graph.html')
    
@app.route('/network/visualisation')
def show_visualisation():
    return send_file('basic_graph.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
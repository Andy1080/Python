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
from flask import Flask, request, send_file
#import csv

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

    startDate =  request.args.get('startDate')
    endDate =  request.args.get('endDate')   
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
    startDate = now - timedelta(days=28)
    startDate = startDate.strftime("%Y-%m-%d")
    symbols = ["BABA","AMZN","MSFT","YHOO", "GOOG","IBM","BK","AXP","EBAY",
                 "FB", "MER", "GS", "C", "JPM", "HPQ", "KO"]
    
    #with open('snp100.text','r') as w:
    #    w_rows = csv.reader(w, delimiter='\t')
    #    companyLookUp = {symbol:name for symbol,name in w_rows}
    #    symbols = companyLookUp.keys()
    
    entries = {}
    for symbol in symbols:    
        query = 'select * from yahoo.finance.historicaldata where symbol in ("{}") and startDate = "{}" and endDate = "{}"'.format(symbol,startDate,endDate)
        payload = {'q':query,
               'env':API_ENV,
               'format':API_FORMAT,
               'callback': API_CALLBACK}               
        response = rq.get(API_BASE, params=payload).json()
            
        try:
            entries[symbol] = [x['Close'] for x in response['query']['results']['quote']]
        except:
            print response
    
    correlation = np.corrcoef(np.vstack(entries.values()).astype(float))
    companies = entries.keys()
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

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
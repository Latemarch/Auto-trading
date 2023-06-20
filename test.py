import json
import numpy as np
import pandas as pd
import time
import gzip
import plotly.graph_objects as go
import plotly.subplots as ms
import mymodule as mm
import mystrategy as st 

startcode = time.time()
    
candle = pd.DataFrame(columns =['time','open','high','low','close','volume'])
Wallet = {'time':[],'lprofit':[],'sprofit':[],'balance':[100]}
history = {
    'long':{'buy':{'time':[],'price':[]},'sell':{'time':[],'price':[]}},
    'short':{'buy':{'time':[],'price':[]},'sell':{'time':[],'price':[]}},
    'profitcut':0, 'losscut':0
}
localextrema = {
    'maximum':{'time':[],'price':[],'length':[]},
    'minimum':{'time':[],'price':[],'length':[]},'aori':0
}
localextrema_ohlc = {
    'maximum':{'time':[],'price':[],'length':[]},
    'minimum':{'time':[],'price':[],'length':[]},'aori':0
}
position = {'side':0,'size':100,'entry_price':100,'ltime':0,'stime':0,'lbtime':0,'sbtime':0}
Order = {'long':0,'short':0,'lprice':0,'sprice':0}
#indi(0time,1ma1,2ma2,3macd,4macd_sig,5macd_osc)

lin = {'time':[],'mid':[],'top':[],'bot':[]} 

long2_top=0
long1_bot=0
start =0
last = 64
graph = 0
stoporder = 0
z0 ={'time':[],'price':[]} 
for h in range(start,last):

    try:
        with gzip.open('/Users/jun/documents/btcusd/%03d.gz' % h, 'rb') as f:
            data = f.readlines()
    except:
        with gzip.open('D:/tbproject/data/btcusd/%03d.gz' % h, 'rb') as f:
            data = f.readlines()

    daytics = []
    for row in data:
        daytics.append(row.decode('utf-8').split(','))
    
    del daytics[0]
    daytics.reverse()
    tictime = float(daytics[1][0])
    minute = tictime//60

    if h == start:
      price = float(daytics[1][4])
      tictime = float(daytics[1][0])
      minute = tictime//60
      k = 0
      ohlc_list = []
      volume = 0
      ohlc = np.array([[minute,price,price,price,price,price]])
      ohlc = np.delete(ohlc,0, axis=0)
    print(h) 
    for i, row in enumerate(daytics):
        ohlc_list.append(float(row[4]))
        volume += (float(row[3]))

        if tictime == float(row[0]): continue
        else: 
            tictime = float(row[0])
            price = ohlc_list[-1]


        # i min canlde =========================
        if minute != tictime//60:
            k+=1
            minute=tictime//60
            ohlc=mm.addcandle(ohlc,ohlc_list,volume,tictime)
            volume = 0
            ohlc_list = []
            print(k)
        # i min canlde =========================
		
    print(len(ohlc), ohlc[-1])
    with open('/Users/jun/documents/btcusd/%03d.json' % h,'w') as f:
         json.dump(ohlc.tolist(),f)

        
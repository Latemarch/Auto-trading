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
#indi(0time,1ma1,2ma2,3macd,4macd_sig,5macd_osc)

lin = {'time':[],'mid':[],'top':[],'bot':[]} 

permit_long = 0
permit_short= 0
permit_short1= 0
premaxmacd = 0
start =0 
last = 20
graph = 0
Order = 5
stoporder = 0
for h in range(start,last):
    with gzip.open('/Users/jun/btcusd/%03d.gz' % h, 'rb') as f:
        data = f.readlines()

    daytics = []
    for row in data:
        daytics.append(row.decode('utf-8').split(','))
    
    del daytics[0]
    daytics.reverse()

    if h == start:
        price = float(daytics[1][4])
        tictime = float(daytics[1][0])
        minute = tictime//60
        k = 0
        ohlc_list = []
        volume = 0
        ohlc = np.array([[minute,price,price,price,price,price]])
        ohlc = np.delete(ohlc,0, axis=0)
        indicators = {
            'time':np.empty([0]),
            'ma1':np.empty([0]),
            'ma2':np.empty([0]),
            'macd':np.empty([0]),
            'macd_sig':np.empty([0]),
            'macd_osc':np.empty([0])
        }
    print(h) 
    for i, row in enumerate(daytics):
        ohlc_list.append(float(row[4]))
        volume += (float(row[3]))

        if tictime == float(row[0]): continue
        else: 
            tictime = float(row[0])
            price = ohlc_list[-1]
        if ohlc_list[0] - ohlc_list[-1]> 100: 
            Order=-3
            stoporder=1

  

        # i min canlde =========================
        if minute != tictime//60:
            k+=1 
            minute=tictime//60
            ohlc=mm.addcandle(ohlc,ohlc_list,volume,tictime)
            volume = 0
            ohlc_list = []
        # i min canlde =========================
        
            if k < 50: continue 
            #======idicators======
            mm.makingindi(ohlc,indicators,tictime)
            mm.minmax_macd(indicators,localextrema,10)
            mm.linearfit(tictime,ohlc[:,4],lin,40)
            mm.minmax_ohlc(ohlc,localextrema_ohlc,lin,10)
            #======idicators======

            #Order,targetprice = st.macd(tictime,position,indicators,localextrema,price,70,premaxmacd)


            if len(localextrema_ohlc['maximum']['price'])<3:continue
            Order,targetprice = st.minmax1(tictime,position,lin)
            st.exitprice(position,ohlc,localextrema_ohlc)
            jam = st.jammed(ohlc)

            if jam < 10:
                Order =2


            if position['side']==1:
                if price > lin['top'][-1]+20:
                    Order = 2
            elif position['side']==-1:
                if price < position['profitcut']:
                    Order =-2#short_reduceonly_maker
                elif price > position['losscut']:
                    Order =-3#short_reduceonly_taker
                elif indicators['macd_osc'][-2]>0:
                    Order =-3
                elif indicators['macd_osc'][-2]<-30:
                    Order =-3
                elif Order == 1:
                    Order = -2

                        

                

        if k < 50: continue 

        if position['side']==1:
            if Order==2:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
                position['ltime'] = tictime
            elif Order==3:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=True)
                position['ltime'] = tictime
            elif price < position['losscut']:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=True)
                position['ltime'] = tictime
            elif price > position['profitcut']:
                Order = 2#long_reduceonly_maker
                #targetprice = position['profitcut']
        elif position['side']==-1:
            if Order==-2:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
                position['stime'] = tictime
            elif Order==-3:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=True)
                position['stime'] = tictime
        else:
            if Order == 1 and price <= targetprice:
                mm.Order_Limit('long',position,history,price,tictime,lin)
            elif Order == -1 and price >= targetprice:
                mm.Order_Limit('short',position,history,price,tictime,lin)
            elif Order == 11:
                if price<=targetprice:
                    mm.Order_Limit('long',position,history,price,tictime,lin)





        
        
if graph:
    ohlc_max = np.array(localextrema_ohlc['maximum']['price'])
    ohlc_max = ohlc_max + 100
    ohlc_min = np.array(localextrema_ohlc['minimum']['price'])
    ohlc_min = ohlc_min - 100
                    
    df, candle = mm.candle_go(ohlc)
    fig = ms.make_subplots(rows=2,cols=1,shared_xaxes=True,shared_yaxes=False,vertical_spacing=0.02)
    ma10=go.Scatter(x=indicators['time'],y=indicators['ma1'],line=dict(color='blue',width=0.8),name='ma10')
    lin_top =go.Scatter(x=lin['time'],y=lin['top'],line=dict(color='red',width=0.8),name='lintop')
    lin_mid=go.Scatter(x=lin['time'],y=lin['mid'],line=dict(color='red',width=0.8),name='lintop')
    lin_bot=go.Scatter(x=lin['time'],y=lin['bot'],line=dict(color='red',width=0.8),name='lintop')
    history_SL = go.Scatter(x=history['long']['sell']['time'], y=history['long']['sell']['price'], mode ="markers", marker=dict(size =20,color='green',symbol= '6'), name='Sell long')
    history_BL = go.Scatter(x=history['long']['buy']['time'], y=history['long']['buy']['price'], mode ="markers", marker=dict(size = 20, color='red',symbol= '5'), name='buy long')
    ohlc_max = go.Scatter(x=localextrema_ohlc['maximum']['time'], y=ohlc_max, mode ="markers", marker=dict(size =20,color='green',symbol= '6'), name='Sell long')
    ohlc_min = go.Scatter(x=localextrema_ohlc['minimum']['time'], y=ohlc_min, mode ="markers", marker=dict(size =20,color='red',symbol= '5'), name='Sell long')
    MACD_Oscil = go.Bar(x=indicators['time'], y=indicators['macd_osc'], marker_color='red', name='MACD_Oscil')
    volume= go.Bar(x=df.index, y=df['volume'], marker_color='black', name='Volume')

    fig.update_layout(title='BTCUSD', xaxis1_rangeslider_visible=False)
    fig.add_trace(lin_top,row=1,col=1)
    fig.add_trace(lin_mid,row=1,col=1)
    fig.add_trace(lin_bot,row=1,col=1)
    fig.add_trace(candle, row=1,col=1)
    fig.add_trace(history_SL,row=1,col=1)
    fig.add_trace(history_BL,row=1,col=1)
    #fig.add_trace(ohlc_max,row=1,col=1)
    #fig.add_trace(ohlc_min,row=1,col=1)
    fig.add_trace(MACD_Oscil,row=2,col=1)
    fig.show()


#print(localextrema['maximum']['length'])
print("time :",time.time()-startcode)


#mm.profitrate(Wallet)
mm.extremadist(localextrema)
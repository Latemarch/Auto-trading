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
last = 20
graph = 1
stoporder = 0
z0 ={'time':[],'price':[]} 
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
    #print(h) 
    init_bal= Wallet['balance'][-1]
    init_pri= price
    for i, row in enumerate(daytics):
    
        ohlc_list.append(float(row[4]))
        volume += (float(row[3]))

        if tictime == float(row[0]): continue
        else: 
            tictime = float(row[0])
            price = ohlc_list[-1]

        if ohlc_list[0] - ohlc_list[-1]> 100: 
            Order['long']=0
            stoporder=1
        

  

        # i min canlde =========================
        if minute != tictime//60:
            '''
            if long2_top:
                long2_top=0
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
                position['stime'] = tictime
            '''
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
            mm.minmax_ohlc(ohlc,localextrema_ohlc,lin,10)
            z0['time'].append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(tictime))))
            z0['price'].append(mm.linearfit(tictime,ohlc[:,4],lin,25))
            
            #======idicators======

            #Order,targetprice = st.macd(tictime,position,indicators,localextrema,price,70,premaxmacd)


            #======strategy========
            if len(localextrema_ohlc['maximum']['price'])<3:continue
            st.minmax1(tictime,position,lin,Order)
            #st.exitprice(position,ohlc,localextrema_ohlc)


            #vol = mm.vol_vol(ohlc)
            #if vol[3]<0 or vol[2]<0:
            #    Order['long']=0


            jam = st.jammed(ohlc)
            if jam < 10:
                if position['side']==1:Order['long'] = 2
                Order['long'] = 0

            #======strategy========


                

        if k < 50: continue 
        if long2_top:
            if indicators['macd_osc'][-1]<indicators['macd_osc'][-2] or indicators['macd_osc'][-1]>100:
                long2_top=0
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
                position['ltime'] = tictime
            else: continue
        elif long1_bot:
            if indicators['macd_osc'][-1]>indicators['macd_osc'][-2]:# and z0['price'][-1]<-10:
                long1_bot=0
                mm.Order_Limit('long',position,history,price,tictime,Order)



        if position['side']==1:
            if Order['long']==2:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
                position['ltime'] = tictime
            elif price > lin['top'][-1]+50:
                long2_top=1
            elif indicators['macd_osc'][-1]>50:
                long2_top=1
            elif price < position['losscut']:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=True)
                position['ltime'] = tictime
            elif price > position['profitcut']:
                long2_top=1
                #mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
        elif position['side'] == -1:
            if Order['short']==2:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
                position['stime'] = tictime
            elif Order['short']==3:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=True)
                position['stime'] = tictime
            #elif price < lin['bot'][-1]:
            #    mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
            elif price > position['losscut']:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=True)
                position['stime'] = tictime
            elif price < position['profitcut']:
                mm.Order_Reduceonly(Wallet,position,history,price,tictime,Taker=False)
                position['stime'] = tictime
        else:
            if Order['long']==1 and price<=Order['lprice']:
                long1_bot = 1
                #mm.Order_Limit('long',position,history,price,tictime,Order)
            if Order['short']==1 and price>=Order['sprice']:
                mm.Order_Limit('short',position,history,price,tictime,Order)

    print(h,round((Wallet['balance'][-1]-init_bal)/init_bal*100,2),round((price-init_pri)/init_pri*100,2))


        
        
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
    lin_bot=go.Scatter(x=lin['time'],y=lin['bot'],line=dict(color='blue',width=0.8),name='lintop')
    z00=go.Scatter(x=z0['time'],y=z0['price'],line=dict(color='blue',width=0.8),name='z0')

    history_SS = go.Scatter(x=history['short']['sell']['time'], y=history['short']['sell']['price'], mode ="markers", marker=dict(size =20,color='black',symbol= '5'), name='Sell short')
    history_BS = go.Scatter(x=history['short']['buy']['time'], y=history['short']['buy']['price'], mode ="markers", marker=dict(size = 20, color='white',symbol= '6'), name='buy short')
    history_SL = go.Scatter(x=history['long']['sell']['time'], y=history['long']['sell']['price'], mode ="markers", marker=dict(size =20,color='green',symbol= '6'), name='Sell long')
    history_BL = go.Scatter(x=history['long']['buy']['time'], y=history['long']['buy']['price'], mode ="markers", marker=dict(size = 20, color='red',symbol= '5'), name='buy long')

    for i,row in enumerate(localextrema_ohlc['maximum']['time']):
        localextrema_ohlc['maximum']['time'][i]=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(row)))

    ohlc_max = go.Scatter(x=localextrema_ohlc['maximum']['time'], y=ohlc_max, mode ="markers", marker=dict(size =20,color='green',symbol= '6'), name='Sell long')
    ohlc_min = go.Scatter(x=localextrema_ohlc['minimum']['time'], y=ohlc_min, mode ="markers", marker=dict(size =20,color='red',symbol= '5'), name='Sell long')
    MACD_Oscil = go.Bar(x=indicators['time'], y=indicators['macd_osc'], marker_color='red', name='MACD_Oscil')
    volume= go.Bar(x=df.index, y=df['volume'], marker_color='black', name='Volume')

    fig.update_layout(title='BTCUSD', xaxis1_rangeslider_visible=False)
    fig.add_trace(candle, row=1,col=1)
    fig.add_trace(lin_top,row=1,col=1)
    fig.add_trace(lin_mid,row=1,col=1)
    fig.add_trace(lin_bot,row=1,col=1)
    fig.add_trace(history_SL,row=1,col=1)
    fig.add_trace(history_BL,row=1,col=1)
    fig.add_trace(history_SS,row=1,col=1)
    fig.add_trace(history_BS,row=1,col=1)
    #fig.add_trace(ohlc_max,row=1,col=1)
    #fig.add_trace(ohlc_min,row=1,col=1)
    fig.add_trace(MACD_Oscil,row=2,col=1)
    fig.add_trace(z00,row=2,col=1)
    fig.show()

#Elapsed Time
print("time :",time.time()-startcode)

# 
if Wallet['lprofit']:
    lprofit =np.array(Wallet['lprofit'])
    sum = 0
    for i,row in enumerate(lprofit):
        if row < -3: sum+=1
    print('Long:',round(np.mean(lprofit),3),'//',round(np.std(lprofit),3),sum/len(lprofit))
if Wallet['sprofit']:
    sprofit =np.array(Wallet['sprofit'])
    print('Short:',round(np.mean(sprofit),3),'//',round(np.std(sprofit),3))
mm.profitrate(Wallet)
#mm.extremadist(localextrema)
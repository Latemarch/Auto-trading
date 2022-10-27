import numpy as np
import pandas as pd
import gzip
import math
import mplfinance as mpf
import pandas as pd
import time
import datetime
import plotly.graph_objects as go
import plotly.subplots as ms

from pandas.core.frame import DataFrame
#mac

startcode = time.time()

def trading(position, buyorsell):
    i = 1 if position == 'long' else 0
    stoploss[i] = k
    if buyorsell == 'buy':
        balance[i][0] = 1
        balance[i][1] = price
    else:
        balance[i][0] = 0
        add = ((i*2)-1)*(price - balance[i][1])*qty-0.058
        balance[i][2] += add
        if i == 1:
            if add > 0:tradingcountL[0] += 1
            else: 
                tradingcountL[1] +=1
        else:
            if add > 0:tradingcountS[0] += 1
            else: 
                tradingcountS[1] +=1
def record_history(position,bors):
    i = 1 if position == 'long' else 0
    j = 0 if bors == 'buy' else 2
    history[i+j].append([candletime[-1]])
    history[i+j][-1].append(price)
def local_extremum(a,list,maxormin):#a is half-length 
    c = a*2-1
    b = a-1
    i = [0,1,2] if maxormin == 'max' else [1,0,3]#localextrema = [[[0,0]],[[0,0]],[0],[0]]
    if (i[0]==0 and np.argmax(list[-c:]) == b) or (i[0]==1 and np.argmin(list[-c:])==b):
        localextrema[i[0]].append([candletime[-a]])
        localextrema[i[0]][-1].append(list[-a])
        if localextrema[i[1]][-1][0]:
            localextrema[i[2]].append(abs(localextrema[i[0]][-1][1] - localextrema[i[1]][-1][1]))
    '''
    if np.argmin(list[-c:,2]) == b:
        localextrema[1].append([candletime[-a]])
        localextrema[1][-1].append(list[-a])
        if localextrema[0][-1][0]:
            localextrema[3].append(abs(localextrema[0][-1][1] - localextrema[1][-1][1]))
    '''



balance = [[0,0,100],[0,0,100]]
history = [[[0,0]],[[0,0]],[[0,0]],[[0,0]]]
localextrema = [[[0,0]],[[0,0]],[0],[0]]
volume = 0
global k
ohlc_list = []
ohlc = np.empty((1,5))
candletime = []
lenofcandle = []
macd_osc = []
macd = np.empty((0))
k = 0
trend = 0
losstimeL = 0
losstimeS = 0
stoploss =[0,0]
tradingcountS= [0,0]
tradingcountL= [0,0]
start = 0#101 
last = 3#103
graph = 1 #1 true
ma1 = []
ma2 = []
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
        candletime.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(daytics[1][0]))))
        ohlc = np.append(ohlc,[[price,price,price,price,price]],axis =0)
        ohlc = np.delete(ohlc,0, axis = 0)

    qty = 100/price
    pp = price*0.02
    ppl = pp/2
    ppmacd = pp/14
    for i, row in enumerate(daytics):
        if i == 0:
            stime = row[0]
            #print(row[0])
        ohlc_list.append(float(row[4]))
        volume += (float(row[3]))

        # To make bundle of ticdatas having "same" time
        if tictime == float(row[0]): 
            continue
        else:
            tictime = float(row[0])
        # Now, I got the data from the server, 
        # server give me the data bundle which regards datas made similar time as same time 

        # 1 min candle ==================================================
        if minute != tictime//60:
            k+=1
            minute = tictime//60
            candletime.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(tictime))))
            ohlc = np.append(ohlc,[[ohlc_list[0],max(ohlc_list),min(ohlc_list),ohlc_list[-1],volume]],axis = 0)
            lenofcandle.append(max(ohlc_list)-min(ohlc_list))
            volume = 0
            ohlc_list = []
        # 1 min candle ==================================================

        ###### Here, U can write ur strategy. U have bundle of ticdata(got once) from bybit server 
            ma1.append(float(np.mean(ohlc[-12:,3])))
            ma2.append(float(np.mean(ohlc[-26:,3])))
            ma3 = np.mean(ohlc[-50:,3])
            macd = np.append(macd,ma1[-1]-ma2[-1])
            macd_sig = np.mean(macd[-9:])
            macd_osc.append(macd[-1] - macd_sig)
            local_extremum(20,macd_osc,'max')
            local_extremum(20,macd_osc,'min')
            if not k > 50: continue
            #========trying to calculate price making macd 0 and 100 =====
            p_macd0=-25.0714*(0.889*(ma1[-1]-ma2[-1]-ohlc[-12,3]/12+ohlc[-26,3]/26)-macd_sig+macd[-9]/9)
            p_macd100 = p_macd0 + 2507.14
            
            #========trying to calculate price making macd 0 and 100 =====
            if not balance[1][0] and macd_osc[-1] < -ppmacd and stoploss[1]+30<k:# and localextrema[3][-1] > -50:
                permit_long = 1
            else: permit_long = 0

        if not k > 50: continue


        price = float(row[4])
        if balance[1][0]:#and stoploss[1]+20 < k :
            if price < lossprice_L or price > profitprice_L:
                trading('long','sell')
                record_history('long','sell')
            elif macd_osc[-1] > ppmacd:
                trading('long','sell')
                record_history('long','sell')
            #elif localextrema[1][-1][1] < macd_osc[-5] < macd_osc[-1]:
            #    trading('long','sell')
            #    record_history('long','sell')



        if balance[0][0]:#
            if lossprice_s < price or price < profitprice_s: 
                trading('short','sell')
                record_history('short','sell')
            #elif macd_osc[-1] < -ppmacd:
            #    trading('short','sell')
            #    record_history('short','sell')
            elif localextrema[0][-1][1] > macd_osc[-5] > macd_osc[-1]:
                trading('short','sell')
                record_history('short','sell')

        if balance[1][0] or balance[0][0]: continue
        if permit_long and macd_osc[-2]< macd_osc[-1]:
            permit_long = 0
            trading('long','buy')
            record_history('long','buy')
            #print('Long',int(p_macd0-ppmacd*25.0714),int(p_macd0+macd_osc[-1]*25.0714),'/',price)
            profitprice_L = price+pp/2
            lossprice_L = price-ppl
            Lreached = 0

        #if not balance[0][0] and macd_osc[-1]>0 and stoploss[0]+60<k and localextrema[0][-1][1]> ppmacd and p_macd0 >price: 
        if not balance[0][0] and macd_osc[-1]>ppmacd and stoploss[0]+60<k: 
            trading('short','buy')
            record_history('short','buy')
            profitprice_s = price-pp/4
            lossprice_s = price+ppl
    if stime > row[0]:
        print(row[0],h)  


    p1 = tradingcountL[0]+tradingcountL[1]
    p2 = tradingcountS[0]+tradingcountS[1]    
    print(h,'))',round(balance[1][2],2),'(',tradingcountL[0],p1,')',round(balance[0][2],2),'(',tradingcountS[0],p2,')',round(100*(float(daytics[-1][4])-float(daytics[0][4]))/float(daytics[0][4]),2))
    tradingcountS= [0,0]
    tradingcountL= [0,0]





if 1==graph:
    macd_osc.append(macd[-1] - macd_sig)
    #=============== Candle Chart =================
    index = pd.DatetimeIndex(candletime)
    df = DataFrame(data=ohlc, index=index, columns=['open','high','low','close','volume'])
    df = df.astype(float)
    df['ma10'] = df['close'].rolling(12).mean()
    df['ma20'] = df['close'].rolling(26).mean()
    df['ma50'] = df['close'].rolling(120).mean()
    df['MACD'] = df['ma10'] - df['ma20']    # MACD
    df['MACD_Signal'] = df['MACD'].rolling(window=9).mean() # MACD Signal
    df['MACD_Oscil'] = df['MACD'] - df['MACD_Signal']   #MACD 오실레이터
    df['macdcd'] = macd_osc
    df['max'] = np.nan
    df['min'] = np.nan
    df['buy_long'] = np.nan
    df['sell_long'] = np.nan

    for i in range(4): localextrema[i].pop(0)
    for i, val in enumerate(localextrema[0]):
        df.loc[val[0],'max'] = val[1]# + 2
    for i, val in enumerate(localextrema[1]):
        df.loc[val[0],'min'] = val[1]# - 2

    k = 0#select position u wanna see (0=short,1=long)
    for i in range(4): history[i].pop(0)
    for i, val in enumerate(history[k]):
        df.loc[val[0],'buy_long'] = val[1] + 200
    for i, val in enumerate(history[k+2]):
        df.loc[val[0],'sell_long'] = val[1] - 200

    ma10 = go.Scatter(x=df.index, y=df['ma10'], line=dict(color='black', width=0.8), name='ma20')
    ma20 = go.Scatter(x=df.index, y=df['ma20'], line=dict(color='green', width=0.8), name='ma50')
    ma50 = go.Scatter(x=df.index, y=df['ma50'], line=dict(color='red', width=0.8), name='ma120')
    maxval = go.Scatter(x=df.index, y=df['max']+50, mode ="markers", marker=dict(color='green',symbol= '6'), name='Max')
    minval = go.Scatter(x=df.index, y=df['min']-50, mode ="markers", marker=dict(color='red',symbol = '5'), name='Min')
    history_SL = go.Scatter(x=df.index, y=df['sell_long'], mode ="markers", marker=dict(color='green',symbol= '6'), name='Sell long')
    history_BL = go.Scatter(x=df.index, y=df['buy_long'], mode ="markers", marker=dict(color='red',symbol = '5'), name='Buy long')
    candle = go.Candlestick(x=df.index,open=df['open'],high=df['high'],low=df['low'],close=df['close'])
    volume_bar = go.Bar(x=df.index,y=df['volume'], name='volume')
    MACD = go.Scatter(x=df.index, y=df['MACD'], line=dict(color='blue', width=2), name='MACD', legendgroup='group2', legendgrouptitle_text='MACD')
    MACD_Signal = go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(dash='dashdot', color='green', width=2), name='MACD_Signal')
    MACD_Oscil = go.Bar(x=df.index, y=df['MACD_Oscil'], marker_color='red', name='MACD_Oscil')
    #MACD_Oscil = go.Bar(x=df.index, y=df['macdcd'], marker_color='black', name='MACD_Oscil')

    #fig = go.Figure(data=[candle,history_SL,history_BL,ma10,ma20,ma50])
    #fig = go.Figure(data=[candle,ma20,ma50,maxval,minval])
    fig = ms.make_subplots(rows=2, cols=1, shared_xaxes= True,shared_yaxes=False, vertical_spacing=0.02)
    fig.add_trace(candle, row=1,col=1)
    fig.add_trace(ma10, row=1,col=1)
    fig.add_trace(ma20, row=1,col=1)
    fig.add_trace(history_BL, row=1,col=1)
    fig.add_trace(history_SL, row=1,col=1)
    fig.add_trace(maxval, row=2,col=1)
    fig.add_trace(minval, row=2,col=1)
    fig.add_trace(MACD,row=2,col=1)
    fig.add_trace(MACD_Signal,row=2,col=1)
    fig.add_trace(MACD_Oscil,row=2,col=1)
    #fig.add_trace(volume_bar, row=2,col=1)
    fig.update_layout(title='BTCUSD', xaxis1_rangeslider_visible = False)
    #fig.write_image("fig1.svg")
    fig.show()
    '''
    mintomax = np.array(mintomax)
    mintomax = DataFrame(data=mintomax, columns =['mintomax'])
    maxtomin = np.array(maxtomin)
    maxtomin = DataFrame(data=maxtomin, columns =['maxtomin'])
    minmax = pd.concat([mintomax,maxtomin],axis=1)
    minmax.to_excel('minmax1.xlsx')
    df.to_excel('ohlc.xlsx')

    #print(overshooting_short)
    #print(overshooting_long)
    '''


print("time :",time.time()-startcode)











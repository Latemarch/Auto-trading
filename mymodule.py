import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go



def addcandle(ohlc,ohlc_list,volume,tictime):
    #timee = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(tictime)))
    ohlc = np.concatenate((ohlc,[[float(tictime),ohlc_list[0],max(ohlc_list),min(ohlc_list),ohlc_list[-1],volume]]),axis=0)
    return ohlc
    
    
def makingindi(ohlc,indicators,tictime):#indicators(0time,1ma1,2ma2,3macd,4macd_sig,5macd_osc)
    timee = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(tictime)))
    indicators['time'] = np.concatenate((indicators['time'],[timee]),axis=0)
    indicators['ma2'] = np.concatenate((indicators['ma2'],[np.mean(ohlc[-26:,4])]),axis=0)
    indicators['ma1'] = np.concatenate((indicators['ma1'],[np.mean(ohlc[-12:,4])]),axis=0)
    indicators['macd'] = np.concatenate((indicators['macd'],[indicators['ma1'][-1] - indicators['ma2'][-1]]),axis=0)
    indicators['macd_sig'] = np.concatenate((indicators['macd_sig'],[np.mean(indicators['macd'][-9:])]),axis=0)
    indicators['macd_osc'] = np.concatenate((indicators['macd_osc'],[indicators['macd'][-1] - indicators['macd_sig'][-1]]),axis=0)

def Order_Reduceonly(Wallet,position,history,price,tictime,Taker):
    commition=0.00058 if Taker==True else 0.0002
    timee = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(tictime)))
    add = position['side']*(price - position['entry_price'])*position['size']/price-commition*position['size']
    Wallet['balance'].append(Wallet['balance'][-1] + add)
    Wallet['time'].append(timee)
    if position['side']==1:Wallet['lprofit'].append(add)
    elif position['side']==-1:Wallet['sprofit'].append(add)
    
    if position['side'] == 1:
        history['long']['sell']['time'].append(timee)
        history['long']['sell']['price'].append(price)
    else:
        history['short']['sell']['time'].append(timee)
        history['short']['sell']['price'].append(price)
    print(Wallet['time'][-1],round(Wallet['balance'][-1],2),position['side'],round(add,2),'//',price,'ent=',round(position['entry_price'],1),'pro=',round(position['profitcut'],1),'los=',round(position['losscut'],1))
    position['side']=0

    #Wallet.loc[len(Wallet)]=[timee,balance,]

def Order_Limit(side,position,history,price,tictime,lin):
    timee = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(tictime)))
    if side == 'long':
        history['long']['buy']['time'].append(timee)
        history['long']['buy']['price'].append(price)
        position['side'] = 1
        position['entry_price'] = price
        position['profitcut'] = 1.02*price
        position['losscut'] = price*0.99
        position['lbtime']=tictime
    else:
        history['short']['buy']['time'].append(timee)
        history['short']['buy']['price'].append(price)
        position['entry_price'] = price
        position['side'] = -1
        position['profitcut'] = 0.98*price
        position['losscut'] = 1.001*price
        position['sbtime']=tictime
    

def candle_go(ohlc):
    candletime = []
    for row in ohlc:
        candletime.append(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(row[0])))
    index = pd.DatetimeIndex(candletime)
    df = pd.DataFrame(data=ohlc[:,1:], index=index,columns =['open','high','low','close','volume'])
    df=df.astype(float)        
    candle = go.Candlestick(x=df.index,open=df['open'],high=df['high'],low=df['low'],close=df['close'])

    return df,candle

def indicator_go(indicators):
    ma10=go.Scatter(x=indicators['time'],y=indicators['ma1'],line=dict(color='black',width=0.8),name='ma10')
    ma20=go.Scatter(x=indicators['time'],y=indicators['ma2'],line=dict(color='black',width=0.8),name='ma20')

def minmax_ohlc(ohlc,localextrema,lin,a):#a is half-length
    c = a*2-1
    b = a-1
    if np.argmax(ohlc[-c:,2])==b:
        t= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(ohlc[-a,0])))
        localextrema['maximum']['time'].append(t)
        localextrema['maximum']['price'].append(ohlc[-a,2])
        if localextrema['aori'] == -1:
            localextrema['maximum']['length'].append(localextrema['maximum']['price'][-1]-localextrema['minimum']['price'][-1])
        localextrema['aori'] = 1

    if np.argmin(ohlc[-c:,3])==b:
        t= time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(ohlc[-a,0])))
        localextrema['minimum']['time'].append(t)
        localextrema['minimum']['price'].append(ohlc[-a,3])
        if localextrema['aori'] == 1:
            localextrema['minimum']['length'].append(localextrema['maximum']['price'][-1]-localextrema['minimum']['price'][-1])
        localextrema['aori'] = -1


def minmax_macd(list,localextrema,a):#a is half-length
    c = a*2-1
    b = a-1
    if np.argmax(list['macd_osc'][-c:])==b:
        localextrema['maximum']['time'].append(list['time'][-a])
        localextrema['maximum']['price'].append(list['macd_osc'][-a])
        if localextrema['minimum']['price']:
            localextrema['maximum']['length'].append(localextrema['maximum']['price'][-1]-localextrema['minimum']['price'][-1])
    if np.argmin(list['macd_osc'][-c:])==b:
        localextrema['minimum']['time'].append(list['time'][-a])
        localextrema['minimum']['price'].append(list['macd_osc'][-a])
        if localextrema['maximum']['price']:
            localextrema['minimum']['length'].append(localextrema['maximum']['price'][-1]-localextrema['minimum']['price'][-1])

def vol_vol(ohlc):
    list = [0,0,0,0,0,0,0]
    for row in ohlc[-10:]:
        if row[4]-row[1] > 0:
            list[0]+=row[5]
        else: list[0]-=row[5]

    #list[1]=list[0]

    for i in range(1,6):
        j = -i*10
        k = j-10
        for row in ohlc[k:j]:
            if row[4]-row[1]>0:list[i]+=row[5]
            else: list[i]-=row[5]

        list[i+1]=list[i]

    for i,row in enumerate(list):
        list[i]*=0.00000001
        #if row < 0: list[i]=-1
        #else: list[i]=1
    
    return list
                
def linearfit(tictime,ohlc,lin,length):
    lenn = length
    std = np.std(ohlc[-lenn:])
    list = ohlc[-lenn:]
    z=np.polyfit(range(lenn),list,1)
    p=np.poly1d(z)
    timee = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(tictime+60)))
    lin['time'].append(timee)
    mid = p(lenn)
    lin['mid'].append(mid)
    lin['top'].append(mid+std)
    lin['bot'].append(mid-list[-1]*0.002-std)

        
import matplotlib.pyplot as plt
def profitrate(Wallet):
    Wallet['sprofit']=[1]

    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))
    all_data=([(Wallet['lprofit']),(Wallet['sprofit'])])

    # plot violin plot
    axs[0].violinplot(all_data,
                    showmeans=True,
                    showmedians=False)
    axs[0].set_title('Violin plot')

    # plot box plot
    axs[1].boxplot(all_data)
    axs[1].set_title('Box plot')

    # adding horizontal grid lines
    for ax in axs:
        ax.yaxis.grid(True)
        ax.set_xticks([y + 1 for y in range(len(all_data))],
                    labels=['Long', 'Short'])
        ax.set_xlabel('samples')
        ax.set_ylabel('Observed values')

    plt.show()


def extremadist(list):

    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))
    all_data=([(list['maximum']['length']),(list['minimum']['length'])])

    # plot violin plot
    axs[0].violinplot(all_data,
                    showmeans=True,
                    showmedians=False)
    axs[0].set_title('Violin plot')

    # plot box plot
    axs[1].boxplot(all_data)
    axs[1].set_title('Box plot')

    # adding horizontal grid lines
    for ax in axs:
        ax.yaxis.grid(True)
        ax.set_xticks([y + 1 for y in range(len(all_data))],
                    labels=['min to max', 'max to min'])
        ax.set_xlabel('samples')
        ax.set_ylabel('Observed values')

    plt.show()









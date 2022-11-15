import numpy as np
import mymodule as mm
import time


def macd(k,position,indicators,localextrema,price,macdlimit,premaxmacd):

    permit_short1 = 0
    permit_long = 0
    permit_short= 0
            

    if not position['side'] and len(localextrema['maximum']['price'])>0:
        #if indicators['macd_osc'][-1] < 100 and indicators['macd_osc'][-2] < indicators['macd_osc']['price'][-1] and position['ltime'] < k-600 :
        if -indicators['macd_osc'][-1] > localextrema['maximum']['price'][-1]*2 > 20 and indicators['macd_osc'][-2]< indicators['macd_osc'][-1]:
            targetprice = price - 1
            permit_long = 1

        elif len(localextrema['maximum']['price']) > 0:
            if localextrema['maximum']['price'][-1] > macdlimit:
                if premaxmacd != localextrema['maximum']['price'][-1]:
                    permit_short1=1
                premaxmacd = localextrema['maximum']['price'][-1]

            if indicators['macd_osc'][-2]>0 and indicators['macd_osc'][-1] < 0 and position['stime']<k-600 and permit_short1:
                permit_short=1
                targetprice = price + 1
    if permit_long:
        return 1,targetprice
    elif permit_short:
        return -1,targetprice
    else: return 0,0


#def minmax(localextrema_ohlc):
#     if 

def exitprice(position,ohlc,extrema):
    exitp = 0
    if position['side'] == 1:
        i = int((ohlc[-1,0]-position['lbtime'])/60)
        if i:
            k =np.argmin(ohlc[-i:,3])
            minprice = ohlc[-i+k,3]
            extrema = np.array(extrema['maximum']['length'][-5:])
            exitp = minprice*1.01#+np.mean(extrema)
            if position['profitcut'] > exitp:
                position['profitcut'] = exitp
    elif position['side'] == -1:
        i = int((ohlc[-1,0]-position['sbtime'])/60)
        if i:
            k =np.argmax(ohlc[-i:,2])
            maxprice = ohlc[-i+k,2]
            extrema = np.array(extrema['minimum']['length'][-5:])
            exitp = maxprice-np.mean(extrema)
            if position['profitcut'] < exitp:
                position['profitcut'] = exitp

def minmax(tictime,position,price,localex_ohlc,lin):

    Order =0
    targetprice = 0
    if not position['side']:
        if localex_ohlc['maximum']['price'][-3]<localex_ohlc['maximum']['price'][-2]<localex_ohlc['maximum']['price'][-1] and price < lin['bot'][-1]:
            if position['ltime']<tictime-600:
                Order =1
                targetprice = lin['bot'][-1]-100

        if localex_ohlc['maximum']['price'][-3]>localex_ohlc['maximum']['price'][-2]>localex_ohlc['maximum']['price'][-1] and price > lin['top'][-1]:
            if position['stime']<tictime-600:
                Order =-1
                targetprice = lin['top'][-1]+100
    return Order, targetprice


def minmax1(tictime,position,lin):
    Order = 0
    tprice= 0
    if not position['side'] and position['ltime']<tictime-1200:
        Order = 1
        tprice = lin['bot'][-1]-100

    return Order,tprice
        
def minmax2(tictime,position,lin):
    Order = 0
    tprice= 0
    if not position['side'] and position['stime']<tictime-600:
        Order = -1
        tprice = lin['top'][-1]+20
    return Order,tprice

def jammed(ohlc):
    y = np.empty([0])
    for _, row in enumerate(ohlc[-5:]):
        y = np.append(y,np.mean(row[1:5]))
    return np.std(y)
    
    
    
        
        

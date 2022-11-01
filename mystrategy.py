import numpy as np
import mymodule as mm
import time


def macd(k,position,indicators,localextrema,price,macdlimit,premaxmacd):

    permit_short1 = 0
    permit_long = 0
    permit_short= 0
            

    if not position['side'] and len(indicators['macd_osc'])>1:
        if indicators['macd_osc'][-1] < -macdlimit and indicators['macd_osc'][-2] < indicators['macd_osc'][-1] and position['ltime'] < k-600 >0:
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
            exitp = minprice+np.mean(extrema)*2
            if position['profitcut'] > exitp:
                position['profitcut'] = exitp
    elif position['side'] == -1:
        i = int((ohlc[-1,0]-position['sbtime'])/60)
        if i:
            k =np.argmax(ohlc[-i:,2])
            maxprice = ohlc[-i+k,2]
            extrema = np.array(extrema['minimum']['length'][-5:])
            exitp = maxprice-np.mean(extrema)*2
            if position['profitcut'] < exitp:
                position['profitcut'] = exitp


        
        

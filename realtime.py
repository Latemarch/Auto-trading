from pybit import inverse_perpetual
import time
import pandas as pd
import numpy as np
import datetime
import asyncio 
import websockets
import json
import time
import hmac

apikey = "EvW4IWaiFzWJDgFmGz"
apisec = "ctzpTH1LJcldPna4JU0WGGl8lV3yt3qtgOVt"
def get_args_secret(_api_key, _api_secrete):
        expires = str(int(round(time.time())+5000))+"000"
        _val = 'GET/realtime' + expires
        signature = str(hmac.new(bytes(_api_secrete, "utf-8"), bytes(_val, "utf-8"), digestmod="sha256").hexdigest())
        auth = {}
        auth["op"] = "auth"
        auth["args"] = [_api_key, expires, signature]
        args_secret = json.dumps(auth)
        return  args_secret

session_auth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com",
    api_key=apikey,
    api_secret=apisec
)
def Order_Market(side_,qty_):
    return session_auth.place_active_order(
        symbol="BTCUSD",
        side=side_,
        order_type="Limit",
        qty=qty_,
        time_in_force="GoodTillCancel"
    )['result']
def Order_Limit(side_,qty_,price_,loss_):
    return session_auth.place_active_order(
        symbol="BTCUSD",
        side=side_,
        order_type="Limit",
        qty=qty_,
        price = price_,
        stop_loss = loss_,
        time_in_force="GoodTillCancel"
    )['result']
def Order_Reduceonly(side_,qty_,price_):
    return session_auth.place_active_order(
        symbol="BTCUSD",
        side=side_,
        order_type="Limit",
        qty=qty_,
        price = price_,
        time_in_force="GoodTillCancel",
        reduce_only =True 
    )['result']
#result = Order_Market("Buy",1)
#print(result['price'],result['qty'])

session_auth.cancel_all_active_orders(symbol="BTCUSD")
#Got the data past 100 mins
ohlc = np.empty((1,5))
ohlc = np.append(ohlc,[[10,10,10,10,10]],axis =0)
ohlc = np.delete(ohlc,0, axis = 0)
macd = np.empty((0))



session_unauth = inverse_perpetual.HTTP(endpoint="https://api.bybit.com")
ohlc_data= session_unauth.query_kline(
    symbol="BTCUSD",
    interval="1",
    from_time= str(int(time.time() - 60*100))
)

df = pd.DataFrame.from_dict(ohlc_data['result'])
df.set_index('open_time',inplace=True)
for i in range(len(df)):
    open= float(df.iloc[i]['open'])
    high= float(df.iloc[i]['high'])
    low= float(df.iloc[i]['low'])
    close= float(df.iloc[i]['close'])
    volume = float(df.iloc[i]['volume'])
    ohlc = np.append(ohlc,[[open,high,low,close,volume]],axis=0)

ohlc = np.delete(ohlc,-1, axis = 0)
ma1 = []
ma2 = []
macd_osc = []
macd = np.empty((0))
for i in range(30,0,-1):
    ma1.append(float(np.mean(ohlc[-12-i:,3])))
    ma2.append(float(np.mean(ohlc[-26-i:,3])))
    macd = np.append(macd,ma1[-1]-ma2[-1])
macd_sig = np.mean(macd[-9:])
macd_osc.append(macd[-1] - macd_sig)

pp = ohlc[-1,3]*0.02
ppl = pp/2
ppmacd = pp/20
k = 0
preposition = session_auth.my_position(symbol="BTCUSD")['result']
preequity = session_auth.get_wallet_balance(coin="BTC")['result']['BTC']['equity']
losscount = 0
stoplong = -100
#=============================
async def my_loop_WebSocket_bybit(macd,ohlc,ma1,ma2,macd_osc,k,preposition,preequity,losscount,stoplong):
    min = 0
    async with websockets.connect("wss://stream.bybit.com/realtime") as websocket:
        print("Connected to bybit WebSocket")
        await websocket.send('{"op":"subscribe","args":["klineV2.1.BTCUSD"]}')
        data_rcv_response = await websocket.recv() 
        print("response for subscribe req. : " + data_rcv_response)

        while True:
            data_rcv_strjson = await websocket.recv() 
            data_rcv_dict = json.loads(data_rcv_strjson)
            data_trade_list = data_rcv_dict.get('data',0) 
            if data_trade_list == 0:
                continue
            for data_trade_dict in data_trade_list:
                if data_trade_dict['confirm'] == True:
                    data = data_trade_dict
                else: continue 
                k+=1
                #Finding "confirm == Ture" and, once finding, following code is working but 'break' makes following code doesn't work twice in same 'data bundle' 
                #print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(data['start']))))
                ohlc=np.append(ohlc,[[float(data['open']),float(data['high']),float(data['low']),float(data['close']),float(data['volume'])]],axis=0)
                price = ohlc[-1,3]
                #========= Trading Strategy ============#
                position = session_auth.my_position(symbol="BTCUSD")['result']
                active_order = session_auth.get_active_order(symbol = "BTCUSD",order_status ="New")["result"]['data']
                if len(active_order) > 1:
                    session_auth.cancel_all_active_orders(symbol="BTCUSD")

                if preposition['side'] == "Buy" and position['side'] == "None":
                    stoplong = k
                    equity = session_auth.get_wallet_balance(coin="BTC")['result']['BTC']['equity']
                    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(float(data['start']))))
                    print(equity,'/',round(1-equity/preequity,2))
                    if equity < preequity:
                        losscount += 1
                    else:
                        losscount -= 1
                    if losscount > 10:
                        break
                    preequity = equity

                ma1.append(float(np.mean(ohlc[-12:,3])))
                ma2.append(float(np.mean(ohlc[-26:,3])))
                macd = np.append(macd,ma1[-1]-ma2[-1])
                macd_sig = np.mean(macd[-9:])
                macd_osc.append(macd[-1] - macd_sig)
                #p_macd0=-25.0714*(0.889*(ma1[-1]-ma2[-1]-ohlc[-12,3]/12+ohlc[-26,3]/26)-macd_sig+macd[-9]/9)
                
                
                if position['side'] == "None":
                    if active_order:
                        session_auth.cancel_all_active_orders(symbol="BTCUSD")
                        time.sleep(1)

                    if macd_osc[-1] < -ppmacd and stoplong + 50 < k:
                        Order_Limit("Buy",10,price-1,int(price*0.99))
                        time.sleep(1)
                        print("Place Order")
                    else:
                        if min>macd_osc[-1]: min=macd_osc[-1]
                        print(min, macd_osc[-1],'/',-ppmacd)

                elif position['side'] == 'Buy':
                    if position['size'] != 10:
                        session_auth.cancel_all_active_orders(symbol="BTCUSD")
                        time.sleep(1)
                    if not active_order:
                        Order_Reduceonly("Sell",position['size'],max(int(float(position["entry_price"])*1.01),price+1))
                        time.sleep(1)
                preposition = position
                    

                    
                
                #========= Trading Strategy ============#
                break#prevent finding "confirm == True" in same data bundle 


            

##### main exec 
my_loop = asyncio.get_event_loop();  
my_loop.run_until_complete(my_loop_WebSocket_bybit(macd,ohlc,ma1,ma2,macd_osc,k,preposition,preequity,losscount,stoplong)); # loop for connect to WebSocket and receive data. 
my_loop.close(); 
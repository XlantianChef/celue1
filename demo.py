#经过验证此策略有一定的可行性

import websocket, json
import requests
import time 
import strategy  
from consts import *
 
headers = { 
    'X-MBX-APIKEY': api_key 
}
    
order = strategy.Order() 
data = strategy.Data()
 
order_list = [] 
ma_144 = 1000000

global reconnect_count
global ws
ws=None
reconnect_count=0
   
def all_cancel():
    for i in order_list[:]:
        quantity = data.get_positionNum(i)   
        order.market_short(i, quantity, 'long') 
   
def get_listenKey():
    url = 'https://fapi.binance.com/fapi/v1/listenKey' 
    r = requests.post(url=url, headers=headers).json() 
    print(r) 
 
def put_listenKey():
    url = 'https://fapi.binance.com/fapi/v1/listenKey' 
    r = requests.put(url=url, headers=headers).json()    

get_listenKey()    
# delete_listenKey()

def on_open(ws):
    # 建立连接后执行此方法
    print("Connection established.",time.strftime("%Y-%m-%d %H:%M:%S"))  
    subscribe_data = {
        'method': 'SUBSCRIBE',
        'params': params_open,
        'id': 1
    } 
    subscribe_data = json.dumps(subscribe_data) 
    ws.send(subscribe_data)

def on_close():
    # 关闭连接后执行此方法
    print("Connection closed.",time.strftime("%Y-%m-%d %H:%M:%S"))

def on_message(ws, message):
    # 收到消息后执行此方法  
    global balance_open 
    global ma_144
    try: 
        message = json.loads(message) 
        if len(message) >= 3:
            if message['e'] == 'ORDER_TRADE_UPDATE':
                pass
            elif message['e'] == 'ACCOUNT_UPDATE':  
                pass
            else:     
                try:
                    i = message['s'] 
                except:
                    print("messag错误",message, time.strftime("%Y-%m-%d %H:%M:%S"), '\n')
                    message = {'k':{'h':1,'l':1},'s':'BTCUSDT'}
                    i = 'BTCUSDT' 
                close = float(message['k']['c']) 
                # print(message) 
                if int(time.time())%500 == 0:
                    put_listenKey()
                    time.sleep(1)
                if int(time.time())%9 == 0:  
                    ma_144 = data.get_ma(i,'5m',144)
                    time.sleep(1)    
                if close >= ma_144*1.01 and i not in order_list:  
                    quantity = data.get_float(i, float3_list, float2_list, float1_list, balance_open, close)
                    order.market_buy(i,quantity,'long') 
                    order_list.append(i)
                elif close < ma_144 and i in order_list[:]:    
                    quantity = data.get_positionNum(i)
                    order.market_short(i,quantity,'long')
                    order_list.remove(i)  
        else:
            print(message) 
    except Exception as e: 
        print('发生了一个错误', e.__class__.__name__,e, e.__traceback__.tb_lineno, time.strftime("%Y-%m-%d %H:%M:%S"), '\n')
        time.sleep(2)
        
def on_error(ws, error):
    print("发生了一次错误",error.__class__.__name__,error, error.__traceback__.tb_lineno, time.strftime("%Y-%m-%d %H:%M:%S"),f"on error:{error}") 
    global reconnect_count
    print(type(error))
    print(error)
    time.sleep(5)  
    if (type(error)==ConnectionRefusedError or type(error)==websocket._exceptions.WebSocketConnectionClosedException) or ((type(error)==websocket._exceptions.WebSocketTimeoutException or type(error)==ConnectionResetError) or type(error)==TypeError):
        print("正在尝试第%d次重连"%reconnect_count) 
        reconnect_count+=1
        if reconnect_count<100:
            connection_tmp(ws)
    else: 
        print("其他error!") 
        all_cancel()
 
def connection_tmp(ws): 
    ws = websocket.WebSocketApp(f"wss://fstream.binance.com/ws/{listen_key}",
                              on_message = on_message,
                            #   on_data=on_data_test,
                              on_error = on_error,
                              on_close = on_close)
    
    ws.on_open = on_open
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()  
    except:
        ws.close() 

connection_tmp(ws)






 
    

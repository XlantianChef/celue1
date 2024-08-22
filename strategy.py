# -*- coding:utf-8 -*-
#

import requests
import pandas as pd
import hashlib
import hmac
import time  
from consts import *
 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    'X-MBX-APIKEY': api_key
}

def hashing(query_string):
    return hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

class Data:  
    def get_positionNum(self, symbol):
        url = f'{base_url}/v2/account'
        timestamp = int(round(time.time() * 1000))
        query_string = 'timestamp=%s&recvWindow=10000' % str(timestamp)
        signature = hashing(query_string)
        params = {
            'timestamp': timestamp,
            'recvWindow':10000,
            'signature': signature
        }
        try:
            response = requests.get(url=url,headers=headers,params=params).json() 
            if len(response) <= 5:
                time.sleep(3)
                response = requests.get(url=url,headers=headers,params=params).json() 
                if len(response) <= 5:
                    time.sleep(3)
                    response = requests.get(url=url,headers=headers,params=params).json() 
                    print("获取数量时出现了错误",symbol, time.strftime("%Y-%m-%d %H:%M:%S"), response, '\n')
        except:
            time.sleep(3)
            print("获取数量时出现了错误",symbol, time.strftime("%Y-%m-%d %H:%M:%S"), response, '\n')
            response = requests.get(url=url,headers=headers,params=params).json() 
        df = pd.DataFrame(response['positions']) 
        df = df[['symbol', 'positionAmt']]
        df = df.set_index('symbol') 
        df = df.to_dict()
        number = df['positionAmt'][symbol] 
        return abs(float(number))  
         
        
    def get_ma(self, symbol,interval, number):
        url = f'{base_url}/v1/klines?symbol=%s&interval=%s&limit=%s' % (symbol, str(interval), str(number))
        try:
            r = requests.get(url=url, headers=headers, timeout=5).json()
        except:
            time.sleep(2)
            r = requests.get(url=url, headers=headers, timeout=5).json()
        df = pd.DataFrame(r)
        df = df.drop(columns=[5, 6, 7, 8, 9, 10, 11])
        df.columns = ['opentime', 'open', 'high', 'low', 'close']
        close_price = list(map(float, df['close']))
        ma_i = sum(close_price) / number
        return ma_i      

    def get_float(self, symbol, float3_list, float2_list, float1_list, balance_open, price):
        if symbol in float3_list:
            quantity = round((balance_open/price)+0.0005, 3)
        elif symbol in float2_list:
            quantity = round((balance_open/price)+0.005, 2)
        elif symbol in float1_list:
            quantity = round((balance_open/price)+0.05, 1)
        else:
            quantity = int(balance_open / price + 0.5)
        return quantity 

class Order:
    def market_short(self, symbol, quantity,flag): #市价开空
        url = f'{base_url}/v1/order'
        timestamp = int(round(time.time() * 1000))
        query_string = 'timestamp=%s&symbol=%s&side=SELL&type=MARKET&quantity=%s' % (str(timestamp), symbol, str(quantity))
        signature = hashing(query_string)
        params = {
            'timestamp': timestamp,
            'signature': signature,
            'symbol': symbol,
            'side': 'SELL',
            'type': 'MARKET',
            'quantity': quantity,
        }
        r = requests.post(url=url, headers=headers, params=params).json() 
        if len(r) <5 :
            pass
        elif flag == "short":
            print('开仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '㊦㊦㊦㊦㊦', r, "\n")
        elif flag == "long":
            print('平仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '       ', r, '\n')
        if len(r) >= 5:
            return r
        else:
            time.sleep(2)
            r = requests.post(url=url, headers=headers, params=params).json()
            # if flag == "short":
            #     print('开仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '㊦㊦㊦㊦㊦', r, "\n")
            # if flag == "long":
            #     print('平仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '       ', r, '\n')
            return r

    def market_buy(self,symbol, quantity,flag): #市价开多
        url = f'{base_url}/v1/order'
        timestamp = int(round(time.time() * 1000))
        query_string = 'timestamp=%s&symbol=%s&side=BUY&type=MARKET&quantity=%s' % (str(timestamp), symbol, str(quantity))
        signature = hashing(query_string)
        params = {
            'timestamp': timestamp,
            'signature': signature,
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': quantity,
        }
        r = requests.post(url=url, headers=headers, params=params).json()
        if len(r) <5 :
            pass
        elif flag == "short":
            print('平仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '        ', r, "\n")
        elif flag == "long":
            print('开仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '㊤㊤㊤㊤㊤', r, '\n')
        if len(r) >= 5:
            return r
        else:
            time.sleep(2)
            r = requests.post(url=url, headers=headers, params=params).json()
            # if flag == "short":
            #     print('平仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '        ', r, "\n")
            # if flag == "long":
            #     print('开仓' + symbol, time.strftime("%Y-%m-%d %H:%M:%S"), '㊤㊤㊤㊤㊤', r, '\n')
            return r
            
            
            
            
            
            
 

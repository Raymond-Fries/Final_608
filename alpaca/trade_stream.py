import pandas as pd
import websocket, json
import psycopg2
from database_interactions import positions_update, transactions_insertion
import os
import redis
from buy_orders import Buy_Orders
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import time
import datetime
import pytz


def utc_to_local_string(utc_dt):
    timestamp = datetime.datetime.strptime(utc_dt[:-4],"%Y-%m-%dT%H:%M:%S.%f")
    local_tz = pytz.timezone('America/New_York')
    local_dt = timestamp.replace(tzinfo=pytz.utc).astimezone(local_tz)
    ldt = local_tz.normalize(local_dt)
    return datetime.datetime.strftime(ldt ,'%Y-%m-%d %H:%M:%S')

class Trade_Connection:
    
    def on_open(ws):
        
        auth_data = {
            "action": "auth",
            "key": os.environ['AL_AK'],
            "secret": os.environ['AL_SK']
            }

        ws.send(json.dumps(auth_data))

        listen_message = {"action":"listen",
                          "data":{
                              "streams":["trade_updates"]
                              }
                          }
        
        ws.send(json.dumps(listen_message))
        
    def on_message(ws,message):
        red = redis.Redis('localhost',port=6379,db=1, charset="utf-8", decode_responses=True)
        msg = json.loads(message)
        try:
            print(msg['data']['event'])
            if (msg['data']['event'] == 'fill'):
                
                symbol = msg['data']['order']['symbol']
                timestamp = utc_to_local_string(str(msg['data']['order']['created_at']))
                quantity = msg['data']['order']['filled_qty']
                execution_id = msg['data']['execution_id']
                pos_qty = msg['data']['position_qty']
                price = msg['data']['price']
                side = msg['data']['order']['side']
             
                new_msg = {'symbol': symbol,'timestamp': timestamp,'side': side,'quantity': quantity,'position_quantity':pos_qty,'price':price,'side':side} 
                
                try:
                    positions_update(symbol,timestamp,side,str(quantity),str(price),str(pos_qty))
                except Exception as error:
                    print("P error: ",error)
                try:
                   transactions_insertion(symbol,timestamp,side,quantity,execution_id,pos_qty,price)
                except Exception as error:
                    print("T error: ",error)
                try:
                    red.publish('transactions_data', json.dumps(new_msg))
                except Exception as error:
                    print("redis transaction error: ",error)
                    
                        
        except Exception as error:
            print(error)
            
    def on_close(ws):
        print('Connection Closed')

if __name__ == '__main__':
    
    trade_socket = 'wss://paper-api.alpaca.markets/stream'

    trade_ws = websocket.WebSocketApp(trade_socket, on_open = Trade_Connection.on_open,on_message = Trade_Connection.on_message, on_close = Trade_Connection.on_close)
    trade_ws.run_forever()

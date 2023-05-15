import pandas as pd
import websocket, json
import psycopg2
import os
import redis
from database_interactions import intraday_insertion,get_dates
from buy_orders import Buy_Orders
import datetime 
import pytz

def utc_to_local_string(utc_dt):
    timestamp = datetime.datetime.strptime(utc_dt,'%Y-%m-%dT%H:%M:%SZ')
    local_tz = pytz.timezone('America/New_York')
    local_dt = timestamp.replace(tzinfo=pytz.utc).astimezone(local_tz)
    ldt = local_tz.normalize(local_dt)
    return datetime.datetime.strftime(ldt ,'%Y-%m-%d %H:%M:%S')

def get_dates():
    conn = psycopg2.connect(
                host=os.environ['RT_DATABASE_HOST'],
                database=os.environ['RT_DATABASE_NAME'],
                user=os.environ['RT_DATABASE_USER'],
                password=os.environ['RT_DATABASE_PASS'])
    cursor = conn.cursor()
    
    query = 'Select DISTINCT timestamp::date as dates From public.intraday_prices ORDER BY dates ASC;'
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ['dates']
    
    cursor.close()
    conn.close()
    
    return (list(df['dates'])[-2])

class Market_Connection:


        
    def on_open(ws):
        try:
            auth_data = {
                'action':'auth','key': os.environ['AL_AK'] ,'secret':os.environ['AL_SK']}
            
            ws.send(json.dumps(auth_data))

            listen_message = {"action":"subscribe",
                              "bars": ['AAPL','AMD'],
                              }
            
            ws.send(json.dumps(listen_message))
            
        except Exception as e:
            print(e)
        
    def on_message(ws,message):
        
        red = redis.Redis('localhost', port=6379,db=0, charset="utf-8", decode_responses=True)

        msg = json.loads(message)
        dates = get_dates()
        try:
            for d in msg:
                
                if d['T'] == 't':
                    try:
                        timestamp = utc_to_local_string(str(d['t']))
                        new_msg= {"symbol":d['S'],"timestamp":timestamp,"open":d['o'],"high":d['h'],"low":d['l'],"close":d['c']}
                        red.publish('trade_data', json.dumps(new_msg))
                    except Exception as e:
                        print('ms 1 ',e)
                else:
                    try:
                        timestamp = utc_to_local_string(str(d['t']))
                        intraday_insertion(d['S'],timestamp,d['o'],d['h'],d['l'],d['c'])

                        new_msg= {"symbol":d['S'],"timestamp":timestamp,"open":d['o'],"high":d['h'],"low":d['l'],"close":d['c']}
                        Buy_Orders.buy_orders(d['S'],dates)
                        red.publish('intraday_data', json.dumps(new_msg)) 
                        red.publish('alpaca_data',json.dumps({'event': 'intraday','data':new_msg}))
                    except (Exception, psycopg2.DatabaseError) as error:
                        print('ms 2', error)
        except (Exception, psycopg2.DatabaseError) as error:
            print('ms 3 ',error)

    def on_close(ws):
        print('Connection Closed')

if __name__ == '__main__':
    try:
        market_socket = 'wss://stream.data.alpaca.markets/v2/iex'

        market_ws = websocket.WebSocketApp(market_socket, on_open = Market_Connection.on_open,on_message = Market_Connection.on_message, on_close = Market_Connection.on_close)
        market_ws.run_forever()
        
    except Exception as error:
        print(error)

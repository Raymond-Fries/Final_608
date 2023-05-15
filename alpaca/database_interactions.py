import psycopg2
import psycopg2.extras
from psycopg2.extensions import register_adapter, AsIs
import os
import pandas as pd
import redis
import json
from datetime import datetime 
from zoneinfo import ZoneInfo

from psycopg2.pool import ThreadedConnectionPool as _ThreadedConnectionPool
from threading import Semaphore

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
    
    return (list(df['dates']))

def get_symbols():
    con = psycopg2.connect(host=os.environ['RT_DATABASE_HOST'],
                           database=os.environ['RT_DATABASE_NAME'],
                           user=os.environ['RT_DATABASE_USER'],
                           password=os.environ['RT_DATABASE_PASS'])
    cur = con.cursor()
    try:
        sql = 'Select symbol From companies'
        cur.execute(sql)
        df = pd.DataFrame(cur.fetchall())
    

        cur.close()
        con.close()
        return list(df[0])
    except (Exception, psycopg2.DatabaseError) as error:
        print('get symbols ',error)

def transactions_insertion(symbol,timestamp,side,quantity,execution_id,position_quantity,price):
    con = psycopg2.connect(host=os.environ['RT_DATABASE_HOST'],database=os.environ['RT_DATABASE_NAME'],user=os.environ['RT_DATABASE_USER'],password=os.environ['RT_DATABASE_PASS'])
    cur = con.cursor()
    try:
        sql = 'INSERT INTO public.transactions (symbol,timestamp,side,quantity,execution_id,position_quantity,price) VALUES(%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(sql,(symbol,timestamp,side,quantity,execution_id,position_quantity,price,))
        con.commit()
        cur.close()
        con.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print('t1 ',error)


def intraday_insertion(symbol,timestamp,_open,high,low,close):
    
    con = psycopg2.connect(host=os.environ['RT_DATABASE_HOST'],database=os.environ['RT_DATABASE_NAME'],user=os.environ['RT_DATABASE_USER'],password=os.environ['RT_DATABASE_PASS'])
    cur = con.cursor()
    try:
        sql = 'INSERT INTO public.intraday_prices (symbol,timestamp,open,high,low,close) VALUES(%s,%s,%s,%s,%s,%s);'
        cur.execute(sql,(symbol,timestamp,_open,high,low,close))
        con.commit()
        cur.close()
        con.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        print('i1 ',error)
    cur.close()
    con.close()

def positions_update(symbol,timestamp, side,quantity,price,position_quantity):
    red = redis.Redis('localhost',port=6379,db=1, charset="utf-8", decode_responses=True)
    red1 = redis.Redis('localhost',port=6379,db=0, charset="utf-8", decode_responses=True)
    con = psycopg2.connect(host=os.environ['RT_DATABASE_HOST'],database=os.environ['RT_DATABASE_NAME'],user=os.environ['RT_DATABASE_USER'],password=os.environ['RT_DATABASE_PASS'])
    cur = con.cursor()
    try:
        sql = 'Select * From public.positions where symbol = %s'
        cur.execute(sql,(symbol,))

        result = cur.fetchone()
        ots = result[2]
        oq = int(result[4])
        oap = float(result[5])

        if int(position_quantity) == 0:

            p_msg = {'symbol':symbol, 'side':" ",'pos_quantity':0,'average_price':0,'cost':0}
            sql = 'UPDATE public.positions SET  side = %s, pos_quantity=%s, average_price=%s, cost=%s WHERE symbol=%s;'
            cur.execute(sql,(" ",0,0,0,symbol))
            con.commit()
            cur.close()
            con.close()
            red.publish('positions_data', json.dumps(p_msg))
            red1.publish('alpaca_data',json.dumps({'event':'positions','positions_data': p_msg}))

        elif abs(int(position_quantity)) == 100:

            cost = int(position_quantity)*float(price)
            p_msg = {'symbol':symbol,'side':side,'pos_quantity':position_quantity,'average_price':price,'cost':cost}
            
            sql = 'UPDATE public.positions SET side = %s, pos_quantity=%s, average_price=%s, cost=%s WHERE symbol=%s ;'
            cur.execute(sql,(side,position_quantity,price,cost,symbol))
            con.commit()
            cur.close()
            con.close()

            red.publish('positions_data', json.dumps(p_msg))
            red1.publish('alpaca_data',json.dumps({'event':'positions','positions_data':p_msg}))
        
        elif abs(int(position_quantity) > 100):
            nq = oq + int(quantity)
            aep = ((oq * oap)+(int(quantity)*float(price)))/nq
            nc = aep * nq

            p_msg = {'symbol':symbol,'side':side,'pos_quantity':nq,'average_price':aep,'cost':nc}
            
            sql = 'UPDATE public.positions SET side = %s, pos_quantity=%s, average_price=%s, cost=%s WHERE symbol=%s ;'
            cur.execute(sql,(side,nq,aep,nc,symbol))
            con.commit()
            cur.close()
            con.close()
            red.publish('positions_data', json.dumps(p_msg))
            red1.publish('alpaca_data',json.dumps({'event':'positions','positions_data':p_msg}))

    except (Exception, psycopg2.DatabaseError) as error:
        print('p ',error)


def get_positions(symbol):
    con = psycopg2.connect(host=os.environ['RT_DATABASE_HOST'],database=os.environ['RT_DATABASE_NAME'],user=os.environ['RT_DATABASE_USER'],password=os.environ['RT_DATABASE_PASS'])
    cur = con.cursor()
    try:
        sql = 'Select symbol,timestamp From positions where symbol = %s'
        cur.execute(sql,(symbol,))
        result = cur.fetchall()
        d = {'symbol':result[0][0],'timestamp':result[0][1]}
        cur.close()
        con.close()
        return d 
    except (Exception, psycopg2.DatabaseError) as error:
        print('get positions 1 ',error)




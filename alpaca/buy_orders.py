#db imports
import os
import psycopg2
#miscellaneous imports
import pandas as pd

# datetime and time imports
import time
from datetime import datetime as dt
from datetime import date
#alpaca imports
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


#truncates decimals evenly for easy comparison
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier
#places the buy orders
def buy_share_accumulator(company,cycles,api):
    i = 0 
    while i < cycles:
        market_order_data = MarketOrderRequest(symbol=company,qty=100,side=OrderSide.BUY,time_in_force=TimeInForce.FOK)
        api.submit_order(order_data=market_order_data)
        print('Longs '+company+' '+str(dt.now().time()))
        i += 1
#places the short orders
def short_share_accumulator(company,cycles,api):
    i = 0
    while i < cycles:
        market_order_data = MarketOrderRequest(symbol=company,qty=100,side=OrderSide.SELL,time_in_force=TimeInForce.FOK)
        api.submit_order(order_data=market_order_data)
        print('Shorted '+company+' at '+ str(dt.now().time()))
        i += 1
        
#determines when to buy/short       
class Buy_Orders():
    
    def get_dates():
        conn = psycopg2.connect(
                    host=os.environ['RT_DATABASE_HOST'],
                    database=os.environ['RT_DATABASE_NAME'],
                    user=os.environ['RT_DATABASE_USER'],
                    password=os.environ['RT_DATABASE_PASS'])
        cursor = conn.cursor()
        
        query = 'Select DISTINCT timestamp::date as dates From public."Intraday_Prices" ORDER BY dates ASC;'
        cursor.execute(query)
        df = pd.DataFrame(cursor.fetchall())
        df.columns = ['dates']
        
        cursor.close()
        conn.close()
        
        return (list(df['dates'])[-2])
    
    #truncates decimals evenly for easy comparison
    def truncate(n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier
    
    #places the buy orders
    def buy_share_accumulator(company,cycles,api):
        i = 0 
        while i < cycles:
            time.sleep(1)
            market_order_data = MarketOrderRequest(symbol=company,qty=100,side=OrderSide.BUY,time_in_force=TimeInForce.FOK)
            api.submit_order(order_data=market_order_data)
            print('Longs '+company+' '+str(dt.now().time()))
            i += 1
            
    #places the short orders
    def short_share_accumulator(company,cycles,api):
        i = 0
        while i < cycles:
            time.sleep(1)
            market_order_data = MarketOrderRequest(symbol=company,qty=100,side=OrderSide.SELL,time_in_force=TimeInForce.FOK)
            api.submit_order(order_data=market_order_data)
            print('Shorted '+company+' at '+ str(dt.now().time()))
            i += 1

    #determines when to buy/short       
    def buy_orders(company,dates):
        #Gets all of todays minute data for a specific company/symbol
        conn = psycopg2.connect(
                    host=os.environ['RT_DATABASE_HOST'],
                    database=os.environ['RT_DATABASE_NAME'],
                    user=os.environ['RT_DATABASE_USER'],
                    password=os.environ['RT_DATABASE_PASS'])
        cursor = conn.cursor()
        
        query = 'Select symbol,timestamp,close From public.intraday_prices WHERE symbol = %s and timestamp::date >= %s Order By timestamp ASC;'

        cursor.execute(query,(company,str(dates)))
        df = pd.DataFrame(cursor.fetchall())
        df.columns = ['symbol','timestamp','close']
        df['change'] = df['close'].pct_change()
        cursor.close()
        conn.close()

        cl = list(df['close'])
        
        #Connects to alpaca 
        api = TradingClient(os.environ['AL_AK'], os.environ['AL_SK'], paper=True)
        
        #print(company,' time : ',df['timestamp'].iloc[-1],' rsi: ', df['rsi'].iloc[-1])
        if dt.now() > dt.strptime(str(date.today()) +" "+ "09:30:00","%Y-%m-%d %H:%M:%S") and dt.now() < dt.strptime(str(date.today()) +" "+ "15:50:00","%Y-%m-%d %H:%M:%S"):       
            positions = api.get_all_positions()    
            if positions:
                positions_df = pd.DataFrame([{'symbol':p.symbol,'side':p.side,'profitloss_pct':float(p.unrealized_plpc),'profitloss':float(p.unrealized_pl),'avg_entry_price':float(p.avg_entry_price), 'qty':int(p.qty),'asset_id':p.asset_id} for p in positions])
                if positions_df.qty.abs().max() >= 400:
                    above = positions_df.loc[(positions_df['qty'].abs() >= 400)]
                    max_aep = above.loc[(positions_df['avg_entry_price'] == above['avg_entry_price'].max())].reset_index()
                    if company in list(max_aep['symbol']):
                        if max_aep.qty[0] > 0:
                            if (cl[-1] - max_aep['avg_entry_price'][0])/ max_aep['avg_entry_price'][0] < -.0015:
                               Buy_Orders. buy_share_accumulator(company,1,api)
                        elif max_aep.qty[0] < 0:
                            if (cl[-1] - max_aep['avg_entry_price'][0])/ max_aep['avg_entry_price'][0] > .0015:
                                Buy_Orders.short_share_accumulator(company,1,api)
                elif positions_df.qty.abs().max() < 400:
                    if company in list(positions_df['symbol']):
                        holdings = positions_df[positions_df['symbol'] == company].reset_index()
                        if holdings['qty'][0] > 0 and (cl[-1] - holdings['avg_entry_price'][0])/holdings['avg_entry_price'][0] < -.0015:
                            Buy_Orders.buy_share_accumulator(company,1,api)
                        elif holdings['qty'][0] < 0 and (cl[-1] - holdings['avg_entry_price'][0])/holdings['avg_entry_price'][0] > .0015:
                            Buy_Orders.short_share_accumulator(company, 1, api)
                    else:
                        if cl[-1] - cl[-2] < 0 :
                                Buy_Orders.buy_share_accumulator(company, 1, api)
                        elif cl[-1] - cl[-2] > 0:
                                Buy_Orders.short_share_accumulator(company, 1, api)
            else:
                if cl[-1] - cl[-2] < 0 :
                        Buy_Orders.buy_share_accumulator(company, 1, api)
                elif cl[-1] - cl[-2] > 0:
                        Buy_Orders.short_share_accumulator(company, 1, api)

                        
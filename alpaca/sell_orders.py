import pandas as pd
import numpy as np
import os
import time
from datetime import datetime,timedelta,date,timezone

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from database_interactions import get_positions

def sell_orders(api):
    while (datetime.now().time() < datetime.strptime('15:59:00','%H:%M:%S').time()):

        if datetime.now() > datetime.strptime(str(date.today()) +" "+ "09:30:00","%Y-%m-%d %H:%M:%S"):  
            try:
                positions = api.get_all_positions()
                if positions:
                    positions_df = pd.DataFrame([{'symbol':p.symbol,'side':p.side,'profitloss_pct':float(p.unrealized_plpc),'profitloss':float(p.unrealized_pl),'avg_entry_price':float(p.avg_entry_price), 'qty':int(p.qty),'asset_id':p.asset_id} for p in positions])
                    for c in positions_df.to_dict('records'):
                        if c['symbol'] in list(positions_df['symbol']):
                            if c['qty'] > 0:
                                if c['profitloss_pct'] >= .0006:
                                    market_order_data = MarketOrderRequest(symbol=c['symbol'],qty=abs(c['qty']),side=OrderSide.SELL,time_in_force=TimeInForce.FOK)
                                    api.submit_order(order_data=market_order_data)
                                    print('Longs SOLD: ',datetime.now().time(),' ',c['symbol'],' ',c['avg_entry_price'],' ',abs(c['qty']),' ',c['profitloss'])
                            elif c['qty'] < 0:
                                if c['profitloss_pct'] >= .0006:
                                    market_order_data = MarketOrderRequest(symbol=c['symbol'],qty=abs(c['qty']),side=OrderSide.BUY,time_in_force=TimeInForce.FOK)
                                    api.submit_order(order_data=market_order_data)
                                    print('Shorts SOLD: ',datetime.now().time(),' ',c['symbol'],' ',c['avg_entry_price'],' ',abs(c['qty']),' ',c['profitloss'])
                                                          
            except Exception as e:
                print('Sell Orders Error 1: ',e)
        elif datetime.now() > datetime.strptime(str(date.today()) +" "+ "15:58:00","%Y-%m-%d %H:%M:%S"):
            try: 
                positions = api.get_all_positions()
                if positions:
                    positions_df = pd.DataFrame([{'symbol':p.symbol,'side':p.side,'profitloss_pct':float(p.unrealized_plpc),'profitloss':float(p.unrealized_pl),'avg_entry_price':float(p.avg_entry_price), 'qty':int(p.qty),'asset_id':p.asset_id} for p in positions])
                    api.close_all_positions(cancel_orders=True)
                    print('EOD Liquidation: ',positions_df['profitloss'])
            except Exception as e:
                print('Sell Orders Error 2: ',datetime.now(),' ',e)
        time.sleep(1)

if __name__ == '__main__':
    try:
        api = TradingClient(os.environ['AL_AK'], os.environ['AL_SK'], paper=True)
        sell_orders(api)
    except Exception as e:
        print('Sell order error ',datetime.now(),' ',e)
        api = TradingClient(os.environ['AL_AK'], os.environ['AL_SK'], paper=True)
        sell_orders(api)
        

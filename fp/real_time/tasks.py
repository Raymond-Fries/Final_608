from celery import shared_task

from channels.layers import get_channel_layer
import asyncio

import os
from alpaca.trading.client import TradingClient

channel_layer = get_channel_layer()

@shared_task
def trading_account_update():

    trading_client = TradingClient(os.environ['AL_AK'], os.environ['AL_SK'], paper=True)
    ad = trading_client.get_account()
    account = {'account':{'cash':ad.cash ,'buying_power': ad.buying_power ,'equity_now':ad.equity,'beginning_equity':ad.last_equity}}

    loop = asyncio.get_event_loop()
    coroutine = channel_layer.group_send(
                    'real_time_data',
                    {'type':'account_message',
                    'text':account})
    loop.run_until_complete(coroutine)

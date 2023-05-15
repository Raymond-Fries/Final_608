#!/bin/bash
python3 market_stream.py &
python3 trade_stream.py &
python3 sell_orders.py &

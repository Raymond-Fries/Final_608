import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

from datetime import datetime,time 
from datetime import timedelta
import calendar

from alpaca.data import StockHistoricalDataClient,StockBarsRequest, TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass


class DatabasePopulation:
     
    def create_real_time_tables():
        con = psycopg2.connect(host=os.environ['RT_DATABASE_HOST'],
                            database=os.environ['RT_DATABASE_NAME'],
                            user=os.environ['RT_DATABASE_USER'],
                            password=os.environ['RT_DATABASE_PASS'])
        cur = con.cursor()

        try:
            cur.execute("CREATE TABLE companies (symbol VARCHAR(7) PRIMARY KEY);")
            con.commit()
            cur.execute('CREATE TABLE intraday_prices(symbol VARCHAR(7),"timestamp" TIMESTAMP WITHOUT TIME ZONE,open DOUBLE PRECISION,high DOUBLE PRECISION,low DOUBLE PRECISION, close DOUBLE PRECISION, PRIMARY KEY (symbol, "timestamp"), FOREIGN KEY (symbol) REFERENCES companies(symbol) ON DELETE CASCADE);')
            con.commit()
            cur.execute("CREATE TABLE minute_means(symbol VARCHAR(7) ,timestamp TIME WITHOUT TIME ZONE, change DOUBLE PRECISION,change_std DOUBLE PRECISION,standardized_mean DOUBLE PRECISION, PRIMARY KEY (symbol,timestamp), FOREIGN KEY (symbol) REFERENCES companies(symbol) ON DELETE CASCADE);")
            con.commit()        
            cur.execute("CREATE TABLE daily_minute_means(symbol VARCHAR(7), weekday VARCHAR(12) ,timestamp TIME WITHOUT TIME ZONE ,change DOUBLE PRECISION,change_std DOUBLE PRECISION,standardized_mean DOUBLE PRECISION, PRIMARY KEY (symbol,weekday,timestamp), FOREIGN KEY (symbol) REFERENCES companies(symbol) ON DELETE CASCADE);")
            con.commit() 
            cur.execute("CREATE TABLE positions(position_id SERIAL PRIMARY KEY, symbol VARCHAR(7),side VARCHAR(4) DEFAULT ' ',pos_quantity INTEGER DEFAULT 0,average_price DOUBLE PRECISION DEFAULT 0, cost DOUBLE PRECISION DEFAULT 0, FOREIGN KEY (symbol) REFERENCES companies(symbol) ON DELETE CASCADE);")
            con.commit()
            cur.execute("CREATE TABLE transactions(transactions_id BIGSERIAL PRIMARY KEY, symbol VARCHAR(7),timestamp TIMESTAMP WITHOUT TIME ZONE,side VARCHAR(4),quantity INTEGER,execution_id VARCHAR(50), position_quantity INTEGER,price DOUBLE PRECISION, FOREIGN KEY (symbol) REFERENCES companies(symbol) ON DELETE CASCADE);")
            con.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print('creating database ',error)
        
        cur.close()
        con.close()
        
    ## Population of database
    def populate_companies_table(symbols):
        trading_client = TradingClient(os.environ['AL_AK'],os.environ['AL_SK'])
        search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
        assets = trading_client.get_all_assets(search_params)
        assets_dict = [dict(item) for item in assets]

        df = pd.DataFrame.from_records(assets_dict)
        
        conn = psycopg2.connect(
                    host=os.environ['RT_DATABASE_HOST'],
                    database=os.environ['RT_DATABASE_NAME'],
                    user=os.environ['RT_DATABASE_USER'],
                    password=os.environ['RT_DATABASE_PASS'])
        cursor = conn.cursor()
        cursor.execute('Delete From companies')
        conn.commit()
        for s in symbols:
            company_ = df[df['symbol'] == s].reset_index()

            try:
                psycopg2.extras.register_uuid()
                cursor.execute('INSERT INTO public.companies (symbol) VALUES(%s);',(company_['symbol'][0],))

            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
        conn.commit()     
        cursor.close()
        conn.close()

    def populate_intraday_prices_table(symbols):

        years = [2022,2023]
        all_data = pd.DataFrame()
        
        for year in years:
            for month in range(1, 13):
                if year == datetime.now().year and month > datetime.now().month:
                    pass
                else:
                    try:
                        start_date = str(year)+'-'+str(month)+'-01'
                        end_date = str(year)+'-'+str(month)+'-'+str(calendar._monthlen(year,month))
                        
                        for s in symbols:
                            
                            stock_client = StockHistoricalDataClient(os.environ['AL_AK'],os.environ['AL_SK'])
                            request_params = StockBarsRequest(
                                                    symbol_or_symbols=s,
                                                    start=datetime.strptime(start_date,'%Y-%m-%d'),
                                                    end = datetime.strptime(end_date,'%Y-%m-%d'),
                                                    timeframe = TimeFrame.Minute,
                                                    limit = 10000,
                                                    feed='iex'
                                                    )
                            stock_data = stock_client.get_stock_bars(request_params)
                            
                            data = stock_data.df.reset_index()
                            data = data.drop(['volume','trade_count','vwap'],axis=1)
                            all_data = pd.concat([all_data,data])
                    except Exception as e:
                        print('historical ',e)
        all_data = all_data.sort_values(by='timestamp')
                    
        conn = psycopg2.connect(
                    host=os.environ['RT_DATABASE_HOST'],
                    database=os.environ['RT_DATABASE_NAME'],
                    user=os.environ['RT_DATABASE_USER'],
                    password=os.environ['RT_DATABASE_PASS'])
        cursor = conn.cursor()
        
        conn.commit()
        query = 'insert into intraday_prices values(%(symbol)s, %(timestamp)s, %(open)s, %(high)s, %(low)s, %(close)s)'
        execute_batch(cursor,query,all_data.to_dict('records'))
        conn.commit() 
        cursor.close()
        conn.close()

    def populate_minute_means_table(symbols):
        
        conn = psycopg2.connect(
            host=os.environ['RT_DATABASE_HOST'],
            database=os.environ['RT_DATABASE_NAME'],
            user=os.environ['RT_DATABASE_USER'],
            password=os.environ['RT_DATABASE_PASS'])
        cursor = conn.cursor()
        
        start = datetime.strptime('09:30','%H:%M')
        end = datetime.strptime('16:00','%H:%M')

        for symbol in symbols:
            query = 'Select timestamp, close From public.intraday_prices Where symbol=%s and timestamp::time >= %s and timestamp::time <= %s order by timestamp'
            cursor.execute(query,(symbol,"09:30:00","16:00:00",))
            df = pd.DataFrame(cursor.fetchall())
            df.columns=['timestamp','close']
            
            df['change'] = df.close.pct_change()
            
            df = df.dropna(axis=0)       
            
            while start.time() < end.time():
                
                df2 = df[df['timestamp'].dt.time == start.time()].reset_index()
                
                df2 = df2.drop(['index'],axis=1)
                standardized_mean = ((df2['change']-df2['change'].mean())/df2['change'].std()).mean()

                sql = 'INSERT INTO public.minute_means (symbol,timestamp,change,change_std,standardized_mean) VALUES(%s,%s,%s,%s,%s)'
                cursor.execute(sql,(symbol,start.time(),df2['change'].mean(),df2['change'].std(),standardized_mean,))
                conn.commit()

                start += timedelta(minutes=1)
        cursor.close()
        conn.close()

    def populate_daily_minute_means_table(symbols):

        conn = psycopg2.connect(
            host=os.environ['RT_DATABASE_HOST'],
            database=os.environ['RT_DATABASE_NAME'],
            user=os.environ['RT_DATABASE_USER'],
            password=os.environ['RT_DATABASE_PASS'])
        cursor = conn.cursor()
        
        for symbol in symbols:  
            query = "Select to_char(timestamp, 'Day') as day, timestamp, close From public.intraday_prices Where symbol=%s and timestamp::time >= %s and timestamp::time <= %s order by timestamp"
            cursor.execute(query,(symbol,"09:30:00","16:00:00"))
            df = pd.DataFrame(cursor.fetchall())

            df.columns=['day','timestamp','close']
            df['change'] = df.close.pct_change()

            df = df.dropna(axis=0)

            for day in ['Monday','Tuesday','Wednesday','Thursday','Friday']:
                
                start = datetime.strptime('09:30','%H:%M')
                end = datetime.strptime('16:00','%H:%M')
                while start.time() < end.time():
                    
                    df2 = df[(df['timestamp'].dt.time == start.time()) & (df['day'].str.strip() == day)].reset_index()
                    df2 = df2.drop(['index'],axis=1)
        
                    standardized_mean = ((df2['change']-df2['change'].mean())/df2['change'].std()).mean()
                
                    sql = 'INSERT INTO public.daily_minute_means (symbol,weekday,timestamp,change,change_std,standardized_mean) VALUES(%s,%s,%s,%s,%s,%s)'
                    cursor.execute(sql,(symbol,day,start.time(),df2['change'].mean(),df2['change'].std(),standardized_mean,))
                    conn.commit()

                    start += timedelta(minutes=1)
        cursor.close()
        conn.close()

    def populate_positions_table(symbols):

        conn = psycopg2.connect(
                    host=os.environ['RT_DATABASE_HOST'],
                    database=os.environ['RT_DATABASE_NAME'],
                    user=os.environ['RT_DATABASE_USER'],
                    password=os.environ['RT_DATABASE_PASS'])
        cursor = conn.cursor()
        
        for symbol in symbols:

            sql = 'INSERT INTO public.positions (symbol) VALUES(%s)'
            cursor.execute(sql,(symbol,))
            conn.commit() 
        cursor.close()
        conn.close()
        
if __name__ == '__main__':
    
    symbols = ['AAPL','AMD']
    
    DatabasePopulation.create_real_time_tables()

    DatabasePopulation.populate_companies_table(symbols)
    DatabasePopulation.populate_positions_table(symbols)
    DatabasePopulation.populate_intraday_prices_table(symbols)
    DatabasePopulation.populate_minute_means_table(symbols)
    DatabasePopulation.populate_daily_minute_means_table(symbols)

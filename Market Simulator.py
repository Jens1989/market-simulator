# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 19:44:36 2017

@author: jens_
"""

import pandas as pd
import matplotlib.pyplot as plt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt


Column_Labels = ["Year", "Month", "Day", "Symbol", "Order", "Shares"]

Order_File = pd.read_csv("C:\Users\jens_\Dropbox\Jens\Programming\Python Projects\computational investing\Market Simulator order Files\orders.csv", header=None)

del Order_File[6]

Order_File.columns = Column_Labels

Date_Index = []

for j in range(len(Order_File)):
    Date_Index.append(dt.date(Order_File["Year"][j],Order_File["Month"][j],Order_File["Day"][j]))

Order_File.index = Date_Index
   
del Order_File["Year"], Order_File["Month"], Order_File["Day"]  
    
dt_start = Order_File.index[0] - dt.timedelta(3)
dt_end = Order_File.index[-1] + dt.timedelta(1)
Symbols = Order_File["Symbol"].unique()


dt_timeofday = dt.timedelta(hours=16)
c_dataobj = da.DataAccess('Yahoo')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
ldf_data = c_dataobj.get_data(ldt_timestamps, Symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
actual_closes = d_data["close"].values

actual_closes = pd.DataFrame(actual_closes)

Date_Index = []
for i in ldt_timestamps:
    Date_Index.append(i.strftime("%Y-%m-%d"))

actual_closes.index = Date_Index
actual_closes.columns = Symbols

#preparing the values dataframe


values_symbols = list(Symbols)


# Symbols needed as a column
Values = pd.DataFrame(data=0, index=Date_Index, columns = values_symbols)

Order_File.sort_index(inplace = True)

Values.index = [dt.date(*[int(d) for d in x.split('-')]) for x in Values.index]

                
for row in Order_File.iterrows():
    date = row[0]
    sym, order, quant = row[1]
    if order == 'Buy':
        Values[sym].loc[date:] = Values[sym].loc[date] + quant
    elif order == 'Sell':
        if int(Values[sym].loc[date]) >= quant:   
            Values[sym].loc[date:] = Values[sym].loc[date] - quant
        else:
            Values[sym].loc[date:] = Values[sym].loc[date] = - quant
            

#initializing cash amount before trading
Cash = 1000000

for i in Values.iterrows():
    date = i[0]
    q1, q2, q3, q4 = i[1]
    quantities = q1, q2, q3, q4
    share_value = 0
    
    for quantity in enumerate(quantities):
        quantity_difference = Values.diff(1).loc[date,Values.columns[quantity[0]]]
        stock_close = actual_closes.loc[str(date), Values.columns[quantity[0]]]
       
        if quantity[1] >0 and quantity_difference < 0:
            Cash += -quantity_difference * stock_close
            share_value += quantity[1] * stock_close
        
        elif quantity[1] >0 and quantity_difference >0: #we already own stocks, we buy extra
            Cash -= quantity_difference * stock_close
            share_value += quantity_difference * stock_close
            
        elif quantity_difference > 0: #stocks were bought, cash decreases, share value increases
            
            Cash -= quantity[1] * stock_close
            share_value += quantity[1] * stock_close

        elif quantity[1] > 0 and quantity_difference ==0: #no stocks were bought. calculating share value of the portfolio, share_value increases
            share_value += quantity[1] * stock_close

        elif quantity[1] == 0 and quantity_difference > 0: #short stocks were covered, cash decreases, share value as well
            Cash -= quantity_difference * stock_close
      
        elif quantity_difference < 0 and quantity[1] == 0 or quantity[1] >0: #stocks were sold, cash increases, share value decreases
            Cash += -quantity_difference * stock_close
            
    
        elif quantity[1] < 0 and quantity_difference < 0: #stocks were sold short, cash increases, share value as well
            share_value += -quantity_difference * stock_close
        
        elif quantity[1] <0 and quantity_difference == 0: #value of short stocks in portfolio
            share_value += -quantity[1] * stock_close

    portfolio_value = Cash + share_value
    Values.set_value(date, "Portfolio Value", portfolio_value)
        

        
            



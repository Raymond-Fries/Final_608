from django.shortcuts import render
from .models import Companies,IntradayPrices,Transactions,Positions
from .forms import Company_Select_Form
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

import json
import pandas as pd
import numpy as np
import time
from datetime import datetime,timedelta, date


def line_chart(request):
    company_form = Company_Select_Form()
    answer = 'AAPL'
    if request.method == 'POST':
        form = Company_Select_Form(data=request.POST)
        if form.is_valid():
            answer = form.cleaned_data['company_select']
    else:
        form = Company_Select_Form(request.POST)


    q = IntradayPrices.objects.all().filter(symbol = answer).order_by('timestamp').values()

    df = pd.DataFrame.from_dict(q,orient='columns')
    df['timestamp'] = pd.to_datetime(df['timestamp'],unit='s', utc=True).map(lambda x: x.tz_convert('America/New_York'))
    df['ma_twenty'] = df.close.rolling(20).mean()
    df['ma_sixty'] = df.close.rolling(60).mean()
    df2 = df[df['timestamp'].dt.date == datetime.now().date()].reset_index()
    if len(list(df2['timestamp'])) > 60:
        data = {"labels":list(df2['timestamp'].dt.time),"close":list(df2['close']),'ma_twenty':list(df2['ma_twenty']),'ma_sixty':list(df2['ma_sixty'])}
    else:
        data = {"labels":list(df['timestamp'].dt.time)[-60:],"close":list(df['close'])[-60:],'ma_twenty':list(df['ma_twenty'])[-60:],'ma_sixty':list(df['ma_sixty'])[-60:]}

    today = datetime.strftime(datetime.now().date(),'%Y-%m-%d')
    tran= Transactions.objects.all().filter(timestamp__date=today).order_by('-timestamp').values()

    positions = Positions.objects.all().values()
    
    return render(request,template_name="real_time/real_time_page.html",
                    context={'form':form,
                            'chartData': data,
                            'positions':positions,
                            'transactions':tran,
                            })

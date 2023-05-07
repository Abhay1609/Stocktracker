from django.shortcuts import render
from yahoo_fin.stock_info import *
import pandas as pd
import time
import queue
from threading import Thread
from asgiref.sync import sync_to_async,async_to_sync
# Create your views here.
def stockPicker(request):
    stock_picker = tickers_nifty50()
    print(stock_picker)
    return render(request,'mainapp/stockpicker.html',{'stockpicker':stock_picker})
@sync_to_async
def checkAuthentciated(request):
    if not request.user.is_Authenticated:
        return False
    else:
        return True
async def stockTracker(request):
    is_loginned = checkAuthentciated(request)
    if not is_loginned:
        return HttpResponse("LOgin First")
    stockpicker=request.GET.getlist('stockpicker')

    data={}
    available_stocks=tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
           pass
        else:
            return HttpResponse("Error")
    n_threads=len(stockpicker)
    thread_list=[]
    que=queue.Queue()

    start=time.time()

    # for i in stockpicker:
    #
    #     result=get_quote_table(i)
    #     # print(result)
    #
    #     data.update({i: result})
    for i in range(n_threads):
        thread =  Thread(target=lambda q , arg1: q.put({stockpicker[i]:get_quote_table(arg1)}),args=(que,stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()
    for thread in thread_list:
        thread.join()
    while not que.empty():
        result=que.get()
        data.update(result)
    end =time.time()
    time_taken=end-start
    print(time_taken)
    # dfs = []
    #
    # for ticker in stockpicker:
    #     info = get_quote_table(ticker)
    #     df = pd.DataFrame.from_dict(info, orient='index').T
    #     dfs.append(df)
    #
    # result_df = pd.concat(dfs, ignore_index=True)
    print(data)
    return render(request,'mainapp/stocktracker.html',{'data':data,"room_name":"track"})
from celery import shared_task
from yahoo_fin.stock_info  import *
from threading import Thread
import time
import queue
from channels.layers import get_channel_layer
import asyncio
import simplejson as json
@shared_task(bind=True)
def update_stock(self,stockpicker):
    data={}
    available_stocks = tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            stockpicker.remove(i)
    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()

    start = time.time()


    for i in range(n_threads):
        thread = Thread(target=lambda q, arg1: q.put({stockpicker[i]: json.loads(json.dumps(get_quote_table(arg1),ignore_nan = True))}),args=(que, stockpicker[i]))
        #
        # def nan_to_null(x):
        #     print("Iam running")
        #     return None if isinstance(x, float) and math.isnan(x) else x
        #
        # thread=Thread(target=lambda q, arg1: q.put({stockpicker[i]: json.loads(json.dumps(get_quote_table(arg1), default=nan_to_null))}),args=(que, stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()
    for thread in thread_list:
        thread.join()
    while not que.empty():
        result = que.get()
        data.update(result)
    end = time.time()
    channel_layer=get_channel_layer()
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send("stock_track",{
        'type':'send_stock_update',
        'message':data,
    }))

    return 'Done'


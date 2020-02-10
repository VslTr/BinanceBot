from configobj import ConfigObj
from binance.client import Client
from decimal import Decimal
import colorama
import time
from termcolor import colored

colorama.init()  # для отображения цвета в windows cmd
cfg = ConfigObj('config.ini', encoding='utf8')

key = cfg['API']['key']
secret = cfg['API']['secret']
api_key = key
api_secret = secret
client = Client(api_key, api_secret)
coin1 = cfg['PAIR']['coin1']  # первая монета пары (BTC, ETH, USDT)
coin2 = cfg['CURRENCY']['coin2']  # вторая монета пары
print(coin1, '/', coin2)
print('')
TICKER = coin2 + coin1  # TIKER - например пара (BNBBTC)
current_price = client.get_orderbook_ticker(symbol=TICKER)['bidPrice']
pr_ = float(current_price)
pr = Decimal(str(pr_)).as_tuple().exponent * (-1)  # колличество знаков после запятой для vol. coin2 (Asset Precision)
info = client.get_symbol_info(TICKER)
mq = 0  # минимальное кол-во coin2
fl = info['filters']
for x in fl:
    if x.get('minQty') is not None:  # если в перебираемом словаре не будет ключа 'minQty', вернется значение None
        mq = float(x['minQty'])

if mq >= 1:
    mq = 0
elif mq < 1:
    mq = Decimal(str(mq)).as_tuple().exponent * (-1)

# request_open_orders = client.get_open_orders(symbol=TICKER)
# t_history = client.get_my_trades(symbol=TICKER, limit=30)
# t_history.reverse()
# print(f"count orders: {len(t_history)}")

# bought_coins, spent_coins, average = 0, 0, 0

# for q in t_history[1::]:
#        print(q['price'])

# if t_history[1]["isBuyer"] == True:
#     for i in t_history[1::]:
#         if i['isBuyer'] == True:
#             bought_coins += float(i['qty']) # i['qty']  # сколько купили
#             spent_coins += (float(i['qty']) * float(i['price'])) # i['price']  # по какой ставке купили
#         else: break    
#     print(f"Купили всего: {bought_coins} {coin2}")
#     print(f"Потратили всего: {spent_coins} {coin1}")
            
# elif t_history[0]['isBuyer'] == False:
#     print('ПОСЛЕДНИЙ ИСПОЛНЕННЫЙ ОРДЕР НЕ Buy')

# average = spent_coins / bought_coins # усреднение
# sell_percent = cfg['percent-sell']['p4']  # Процент продажи (профит)
# percent = float(average) / 100.0 * float(sell_percent)  # считаем процент продажи
# price_sell_order = round((average + percent), pr)  # считаем цену ордера продажи с учетом процента продажи
# print(f"Усреднение: {average}")
# print(f"Усредненный ордер на продажу: {price_sell_order}")
# print(f"Заработаем: {price_sell_order * bought_coins}")
# for i in trade_history[1::]:
#     if i['isBuyer'] == True: tmp.append(i)
#     else: break

# for j in tmp: print(j)
# print(request_open_orders)
# coin2_volume = trade_history[-1]['qty']
# print(coin2_volume)

# print(trade_history[-1]["isBuyer"])
"""
def min_p(keys):
    lst = []
    req = client.get_open_orders(symbol=TICKER)
    for i in req:
        a = float(i['price'])
        lst.append(a)
    e = min(lst)
    print('{:.8f}'.format(float(e)))
    print(lst)
    for j in req:
        b = float(j['price'])
        if b == e:
            if keys == 'price':
                return b
            elif keys == 'origQty':
                c = float(j['origQty'])
                return c




# print('{:.8f}'.format(float(orders_request())))

def assk():
    www = min_p('price')
    print('{:.8f}'.format(float(www)))


assk()
"""
def buycoin_counting():
    spent_coins, bought_coins = 0, 0 # spent_coins - потрачено монет, bought_coins - куплено
    t_history = client.get_my_trades(symbol=TICKER, limit=20)
    # trade_history (по умолчанию 500, "limit=100" - 100 последних ордеров)
    t_history.reverse() # переворачиваем список, т.к по умолчанию 0-вым берется самый старый ордер(первый)
            
    if t_history[1]["isBuyer"] == True:
        for i in t_history[1::]:
            if i['isBuyer'] == True:
                bought_coins += float(i['qty']) # i['qty']  # сколько купили
                spent_coins += (float(i['qty']) * float(i['price'])) # i['price']  # по какой ставке купили
            else: break
        print(f"Купили всего: {bought_coins} {coin2}")
        print(f"Потратили всего: {spent_coins} {coin1}")

    elif t_history[0]['isBuyer'] == False:
        print('ПОСЛЕДНИЙ ИСПОЛНЕННЫЙ ОРДЕР НЕ Buy')

    return t_history, spent_coins, bought_coins
    
th = buycoin_counting()
# print(f'Потрачено монет {q} Купленно монет: {w}')
print(len(th))

for an in th[0]:
    print(an)
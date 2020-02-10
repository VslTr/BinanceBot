# MyPoloniex_0.1.3.4
# 09.10.18
import datetime
import logging
import logging.config
import time
import colorama

from binance.client import Client
from configobj import ConfigObj
from termcolor import colored
from decimal import Decimal

colorama.init()  # для отображения цвета в windows cmd
cfg = ConfigObj('config.ini', encoding='utf8')
# config_file = "C:\ Users\ trogwar\ Dropbox\ My Folder\ Cod_ing\ PycharmProjects\ MyPoloniex_0001.2.1/config.ini"
key = cfg['API']['key']
secret = cfg['API']['secret']
api_key = key
api_secret = secret
client = Client(api_key, api_secret)

interval_info = cfg['interval-info']['f']
interval_info2 = cfg['interval-info2']['f2']
coin1 = cfg['PAIR']['coin1']  # первая монета пары (BTC, ETH, USDT)
coin2 = cfg['CURRENCY']['coin2']  # вторая монета пары
cc1 = client.get_asset_balance(asset=coin1)  # выбираем доступный баланс первой монеты пары
cc2 = client.get_asset_balance(asset=coin2)  # выбираем доступный баланс второй монеты пары
TICKER = coin2 + coin1  # TIKER - пара
My_List = client.get_open_orders(symbol=TICKER)  # Список открытых ордеров
Sum_Orders = len(My_List)

cp = client.get_orderbook_ticker(symbol=TICKER)['bidPrice']  # current_price
pr_ = float(cp)
pr = Decimal(str(pr_)).as_tuple().exponent * (-1)  # колличество знаков после запятой для vol. coin2 (Asset Precision)
info = client.get_symbol_info(TICKER)
print(f'INFO: {info}')
#  получаем параметры по текущей паре (минимальное кол-во coin2 и знаков после запятой для цены и т.д)
#  precision = info['baseAssetPrecision']  # колличество знаков после запятой для coin2 --- ???????????
coin2_minQty = 0
mq = 0  # минимальное кол-во coin2
fl = info['filters']
for x in fl:
    if x.get('minQty') is not None:  # если в перебираемом словаре не будет ключа 'minQty', вернется значение None
       mq = float(x['minQty'])
       coin2_minQty = mq
       break
if mq >= 1:  # Если mq боьше или равен 1, то mq=0, 0 - для округления до целых
    mq = 0
elif mq < 1:
    mq = Decimal(str(mq)).as_tuple().exponent * (-1)  # Считаем сколько знаков после запятой, mq = (колич. знаков)
    # (*(-1)), что бы число было положительным после экспоненты
print(f"minQty: {mq}")
print('Asset Precision: ', pr)

print(colored('Пара: ' + str(coin1) + ' - ' + str(coin2), 'green', attrs=['bold']))
print(colored('Баланс ' + str(coin1) + ': ' + str(cc1['free']), 'blue', attrs=['bold']))
print(colored('Баланс ' + str(coin2) + ': ' + str(cc2['free']), 'blue', attrs=['bold']))
print(colored('К-во ордеров: ' + str(Sum_Orders), 'blue'))
print(' ')
print(colored('******************************************************************', 'green', attrs=['bold']))
print(' ')
# sys.exit()
cycle = 0
while True:
    def log_start():
        """
        Based on http://docs.python.org/howto/logging.html#configuring-logging
        """
        logging.config.fileConfig('logging.conf')
        logger = logging.getLogger("exampleApp")
        logger.info("")


    """
    def log_stop():
        logging.config.fileConfig ('logging.conf')
        logger = logging.getLogger ("exampleApp")
        logger.info ("Done!")
    """
    print('funcSELL')


    def buycoin_counting():
        spent_coins, bought_coins = 0, 0 # spent_coins - потрачено монет, bought_coins - куплено
        t_history = client.get_my_trades(symbol=TICKER, limit=100)
        # trade_history (по умолчанию 500, "limit=100" - 100 последних ордеров)
        t_history.reverse() # переворачиваем список, т.к по умолчанию 0-вым берется самый старый ордер(первый)
                
        if t_history[0]["isBuyer"] == True:
            for i in t_history:
                if i['isBuyer'] == True:
                    bought_coins += float(i['qty']) # i['qty']  # сколько купили
                    spent_coins += (float(i['qty']) * float(i['price'])) # i['price']  # по какой ставке купили
                else: break

            print(f"Купили всего: {bought_coins} {coin2}")
            print(f"Потратили всего: {spent_coins} {coin1}")

        elif t_history[0]['isBuyer'] == False:
            print('ПОСЛЕДНИЙ ИСПОЛНЕННЫЙ ОРДЕР НЕ Buy')

        return t_history, spent_coins, bought_coins


    def func_sell():
        print(colored('ЗАПУСК МОДУЛЯ ПРОДАЖИ', 'green', attrs=['bold']))

        def cancel_sell_order():
            b, s = [], []  # списки открытых buy и sell ордеров
            all_open_orders = client.get_open_orders(symbol=TICKER)

            for order in all_open_orders:
                if order['side'] == 'BUY': b.append(order['orderId'])
                elif order['side'] == 'SELL': s.append(order['orderId'])

            print(f'BUY: {b} SELL: {s}')
            # len_s = len(s)
            if len(s) != 0:
                cancel = client.cancel_order(symbol=TICKER, orderId=s[0])
                print(f'SELL ОРДЕР {cancel} ЗАКРЫТ')
            else: print('Нет SELL ордеров')

        cancel_sell_order()

        def set_sell_order():
            average = 0
            call_function = buycoin_counting() # Функция вернет кортеж из 3-х элементов
            spent = call_function[1] # потраченные монеты
            bought = call_function[2] # купленные монеты
            average = spent / bought # усреднение

            cfg1 = ConfigObj('config.ini', encoding='utf8')
            sell_percent = cfg1['percent-sell']['p4']  # Процент продажи (профит)
            coin2_balance = client.get_asset_balance(asset=coin2)['free']
            # print(f'Баланс: {round((float(balance)), mq)} тип: {type(balance)}')
            if coin2_balance != bought: 
                print(colored("Баланс не соответсвует колличеству купленных монет !!!", 'red', attrs=['bold']))

            percent = float(average) / 100.0 * float(sell_percent)  # считаем процент продажи
            print(f"Процент продажи: {percent}")
            price_sell_order = round((average + percent), pr)  # считаем цену ордера продажи с учетом процента продажи
            print(f"Цена ордера: {price_sell_order}")
            set_sell_order = client.order_limit_sell(symbol=TICKER, quantity=round((float(bought)), mq),
                                                    price='{:.8f}'.format(float(price_sell_order)))
            # выставляем ордер на продажу, с параметрами: баланс (вся купленная крипта) и цена ордера
            print(colored('Добавлен SELL ордер: ' + str(set_sell_order) + 'blue', attrs=['bold']))
    
        set_sell_order()


    print('funcBUY1')


    def func_buy1():
        cfg2 = ConfigObj('config.ini', encoding='utf8')
        order_vol = cfg2['order_rate']['or']  # ставка (кол. монет) ордера
        current_price = client.get_orderbook_ticker(symbol=TICKER)['bidPrice']
        # Узнаем текущую цену крайнего ордера на покупку
        print('current price: ', current_price)
        increment = cfg2['increment']['i']  # Будет ли использоваться увеличение отступа между ордерами
        increment_step = cfg2['increment_step']['is']  # Шаг инкримента (увеличения размера отступа)
        print(increment, increment_step)
        step_away_from_bids = cfg2['step-1']['p1']  # Отступ первого ордера в % от bids
        step_away_from_orders = cfg2['step-2']['p2']  # Первый отступ между ордерами
        percent = float(current_price) / 100 * float(step_away_from_bids)  # Считаем процент отступа от bids
        order_price = round((float(current_price) - float(percent)), pr)  # Считаем цену для ордера
        print(f"V1!: {round(float(order_vol))}")
        print(f"V2!: {round(float(order_price))}")
        volume = round((float(order_vol) / float(order_price)), mq)
        print('volume: ', volume)
        print(f"order_price: {order_price}")
        # print('order_price: ', '{:.8f}'.format(float(order_price)))
        # Считаем размер первого ордера покупки (на покупку скольки монет будем выставлять ордер)
        set_order = client.order_limit_buy(symbol=TICKER, quantity=(float(volume)),
                                           price=(float(order_price)))
        # set_order = client.order_limit_buy(symbol=TICKER, quantity='{:.8f}'.format(float(volume)),
                                          # price='{:.8f}'.format(float(order_price)))  # выставляем ордер с параметрами
        #  '{:.8f}'.format(float(order_price))  # Переводим число в степени обратно в десятичный вид =>
        # => Когда много  знаков после запятой python переводит число в отрицательную степень (например 1e-8)
        print(set_order)

        cfg_buy_orders = cfg2['amount_orders']['am']  # Количество ордеров
        mtg = cfg2['martingale']['mr']  # Процент увеличения следующего ордера, Мартингейл
        i = 0
        request_orders = client.get_open_orders(symbol=TICKER)[-1]
        last_order_price = request_orders['price']  # Узнаем ставку последнего ордера
        coin2_in_order = request_orders['origQty']
        # Количестов монет (coin2) в ордере
        temp_order_price = float(last_order_price)
        coin2_volume = float(coin2_in_order)

        temp_step = float(step_away_from_orders)
        print('1TempOrderPrice: ', temp_order_price, '1TempVolume: ', coin2_volume)
        while i < (int(cfg_buy_orders) - 1):  # Отнимаем 1 так как счет с 0
            if int(increment) == 1:  # Расчет с увеличением отступа между ордерами
                next_order_price = round((temp_order_price - temp_order_price / 100 * temp_step), pr)
                print('next_order_price: ', '{:.8f}'.format(float(next_order_price)))
                temp_order_price = next_order_price
                temp_step = float(temp_step) + float(increment_step)
                print('temp step: ', temp_step)
                next_coin2_vol = round((float(coin2_volume) + float(coin2_volume) / 100 * float(mtg)), mq)
                # Считаем размер следующего ордера
                print('next_coin2_vol: ', str(next_coin2_vol))
                coin2_volume = next_coin2_vol
                #  coin1_volume = round((next_coin2_vol * next_order_price), mq)
                set_next_order = client.order_limit_buy(symbol=TICKER, quantity='{:.8f}'.format(float(next_coin2_vol)),
                                                        price='{:.8f}'.format(float(next_order_price)))
                print('СОЗДАН ОРДЕР: ', set_next_order)
                i += 1
                time.sleep(1)

            elif int(increment) == 0:  # Расчет с одинаковым отступом между ордерами
                next_order_price = round((temp_order_price - temp_order_price / 100 * step_away_from_orders), pr)
                # Ситаем цену следующего ордера
                print('next_order_price: ', next_order_price)
                temp_order_price = next_order_price
                next_coin2_vol = round((float(coin2_volume) + float(coin2_volume) / 100 * float(mtg)), mq)
                # Считаем размер следующего ордера
                coin2_volume = next_coin2_vol
                print('next_volume: ', str(next_coin2_vol))
                #  coin1_volume = round((next_coin2_vol * next_order_price), mq)
                set_next_order = client.order_limit_buy(symbol=TICKER, quantity='{:.8f}'.format(float(next_coin2_vol)),
                                                        price='{:.8f}'.format(float(next_order_price)))
                # выставляем следующий ордер с параметрами: цена, размер
                print('СОЗДАН ОРДЕР: ', set_next_order)
                i += 1
                time.sleep(1)
            else:
                print('НЕВЕРНЫЙ ПАРАМЕТР increment_step')
                break

        cfg2['last_step'] = {'ls': str(temp_step)}  # Меняем параметр в крнфиге
        cfg2.write()
        time.sleep(float(interval_info))


    print('funcBUY2')


    def func_buy2():  # функция высталяющая ниже ордера на покупку, при условии исполнения buy ордеров
        print('Start BUY2')

        def min_p(keys):  # Функция определения мнимального (дальнего от bids) ордера и его пораметров.
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

        order_price = 0
        request_open_orders = client.get_open_orders(symbol=TICKER)
        sum_orders = len(request_open_orders)
        if sum_orders == 0:
            print('Нет bay ордеров, переход к модулю установки первых ордеров')
            func_buy1()
        else:
            cfg3 = ConfigObj('config.ini', encoding='utf8')
            amount_orders = cfg3['amount_orders']['am']  # Количество ордеров в конфиге
            step_away_from_orders = float(cfg3['step-2']['p2'])  # Первый отступ между ордерами
            mtg = float(cfg3['martingale']['mr'])  # Процент увеличения следующего ордера, Мартингейл
            increment = float(cfg3['increment']['i'])  # Будет ли использоваться увеличение отступа между ордерами
            increment_step = float(cfg3['increment_step']['is'])  # Шаг инкримента (шаг увеличения параметра отступа)
            buy_count = 0
            sell_count = 0

            for order in request_open_orders:  # Счетаем открытые ордера
                if order['side'] == 'BUY':
                    buy_count += 1
                elif order['side'] == 'SELL':
                    sell_count += 1
            print('')

            print('Колличесвто открытых Buy ордеров: ', buy_count)
            print('Колличесвто открытых Sell ордеров: ', sell_count)

            trade_history = client.get_my_trades(symbol=TICKER)  # trade_history (по умолчанию 500 последних ордеров)
            if int(buy_count) < int(amount_orders) and trade_history[-1]["isBuyer"] == True:
                print(colored('ОРДЕР НА ПОКУПКУ БЫЛ ИСПЛНЕН', 'green', attrs=['bold']))
                print(colored('ДОБАВЛЯЕМ ОРДЕРА', 'green', attrs=['bold']))

                if sell_count > 0 and buy_count == 0 and trade_history[-1]["isBuyer"] == True:
                    current_price = client.get_orderbook_ticker(symbol=TICKER)['bidPrice']
                    price_last_buy = trade_history[-1]['price']
                    if current_price < price_last_buy:
                        order_price = current_price
                    elif price_last_buy < current_price:
                        order_price = price_last_buy
                    coin2_volume = trade_history[-1]['qty']
                else:
                    order_price = min_p('price')
                    coin2_volume = min_p('origQty')

                print('coin2_vol1', coin2_volume)  # !!!
                print('coin2_vol2', coin2_volume)  # !!!

                temp_order_price = order_price
                temp_coin_volume = coin2_volume
                temp_step_up = float(cfg3['last_step']['ls'])
                bc = buy_count
                while bc < int(amount_orders):
                    if int(increment) == 1:  # Расчет с увеличением отступа между ордерами
                        new_price = round((float(temp_order_price) - float(temp_order_price) /
                                           100 * float(temp_step_up)), pr)
                        # Считаем цену нового ордера
                        print('order_price ', new_price)
                        new_volume = round((float(temp_coin_volume) + float(temp_coin_volume) / 100 * mtg), mq)
                        # Считаем обьем ордера
                        print('order_vol ', new_volume)
                        coin1_vol = float(new_volume) * float(new_price)
                        print('coin1_vol объем btc для след ордера: ', coin1_vol)
                        balance_coin1 = client.get_asset_balance(asset=coin1)['free']
                        print('cash coin1: ', balance_coin1)
                        if float(balance_coin1) >= float(coin1_vol):
                            s_order = client.order_limit_buy(symbol=TICKER, quantity='{:.8f}'.format(float(new_volume)),
                                                             price='{:.8f}'.format(float(new_price)))
                            # Выставляем ордер
                            print('Добавленый ордер: ' + str(s_order))
                            time.sleep(2)
                        else:
                            print(
                                colored('НЕДОСТАТОЧНО СРЕДСТВ ДЛЯ ДОБАВЛЕНИЯ ОРДЕРА' + ' !!!', 'red', attrs=['bold']))
                            break
                        tt = client.get_open_orders(symbol=TICKER)[-1]
                        temp_order_price = tt['price']
                        temp_coin_volume = tt['origQty']
                        temp_step_up = float(temp_step_up) + float(increment_step)
                        bc += 1
                        time.sleep(2)

                    elif increment == 0:  # Расчет с одинаковым отступом между ордерами
                        new_price = round((temp_order_price - temp_order_price / 100 * step_away_from_orders), pr)
                        # Считаем цену нового ордера
                        print('order_price ', new_price)
                        new_volume = round((temp_coin_volume + temp_coin_volume / 100 * mtg), mq)
                        # Считаем обьем ордера
                        print('order_vol ', new_volume)
                        coin1_vol = float(new_volume) * float(new_price)
                        print('coin1_vol объем btc для след ордера: ', coin1_vol)
                        balance_coin1 = client.get_asset_balance(asset=coin1)['free']
                        print('cash coin1 ', balance_coin1)
                        if float(balance_coin1) >= float(coin1_vol):
                            s_order = client.order_limit_buy(symbol=TICKER, quantity='{:.8f}'.format(float(new_volume)),
                                                             price='{:.8f}'.format(float(new_price)))
                            # Выставляем ордер
                            print('Добавленый ордер: ' + str(s_order))
                            time.sleep(1)
                        else:
                            print(
                                colored('НЕДОСТАТОЧНО СРЕДСТВ ДЛЯ ДОБАВЛЕНИЯ ОРДЕРА' + ' !!!', 'red', attrs=['bold']))
                            break
                        tt = client.get_open_orders(symbol=TICKER)[-1]
                        temp_order_price = tt['price']
                        temp_coin_volume = tt['origQty']
                        bc += 1
                        time.sleep(1)

                    else:
                        print('НЕВЕРНЫЙ ПАРАМЕТР RISE-STEP')
                        break

                cfg3['last_step'] = {'ls': str(temp_step_up)}  # Меняем параметр в конфиге
                cfg3.write()
                print("BUY2 END")


    print('funcBIDS')


    def func_bids():
        print("BIDS START")
        orders = client.get_open_orders(symbol=TICKER)  # Получаем список открытых ордеров
        buy_count = 0
        sell_count = 0
        # проверяем нет ли открытого sell
        for order in orders:  # Счетаем открытые ордера
            if order['side'] == 'BUY':
                buy_count += 1
            elif order['side'] == 'SELL':
                sell_count += 1

        if sell_count > 0:
            print(colored('ОШИБКА, ОТКРЫТ SELL ОРДЕР', 'read', attrs=['bold']))

        elif sell_count == 0 and buy_count > 0:
            sum_open_orders = len(orders)
            cfg4 = ConfigObj('config.ini', encoding='utf8')
            step1 = cfg4['step-0']['p']  # Отступ первого ордера в % от bids
            current_price = client.get_orderbook_ticker(symbol=TICKER)['bidPrice']  # Узнаем текущую цену (bids)
            percent = float(current_price) / 100 * float(step1)
            order_price = float(current_price) - float(percent)  # Считаем цену для ордера с учетом процента
            print('order_price ', order_price)
            order1 = orders[0]['price']
            # Запрашиваем цену превого текущего ордера bay от bids
            print('order1 ', order1)
            if sum_open_orders > 0 and float(order_price) > float(order1):
                print(colored('ПОДТЯГИВАЕМ ОРДЕРА К BIDS', 'blue', attrs=['bold']))
                co = 0
                while co < sum_open_orders:
                    order_id = client.get_open_orders(symbol=TICKER)[0]['orderId']
                    # узнаем номер нулевого ордера в списке
                    client.cancel_order(symbol=TICKER, orderId=order_id)
                    # удаляем нулевой ордер в списке по его номеру на бирже
                    print('Удален ордер N: ' + str(order_id))
                    print('')
                    co += 1
                time.sleep(1)

                print(colored('ЗАПУСК МОДУЛЯ УСТАНОВКИ BUY ОРДЕРОВ', 'green', attrs=['bold']))
                func_buy1()
                time.sleep(1)
            else:
                print(colored('ПОДНЯТИЕ ОРДЕРОВ К BIDS НЕ ТРЕБУЕТСЯ', 'green', attrs=['bold']))
                print("BIDS STOP")
                time.sleep(1)


    print('')
    print(colored('Блок проверки сосотояния и вызова функций', 'yellow', attrs=['bold']))
    print('')
    time_n = datetime.datetime.now()
    print(
        colored('-- Binance ------ Цикл: ' + str(cycle) + ' -- Binance ----------', 'red', 'on_grey', attrs=['bold']))
    print('')
    print(colored('Pair: ' + TICKER + '  ' + time_n.strftime("%d-%m-%Y %H:%M:%S"), 'cyan', 'on_grey'))
    print('')
    time.sleep(1)
    """
    bb1 = client.get_asset_balance(asset=coin1)['free']  # доступный баланс первой монеты пары
    bb2 = client.get_asset_balance(asset=coin2)['free']  # доступный баланс второй монеты пары
    print(colored('Пара: ' + str(coin1) + ' - ' + str(coin2), 'blue', attrs=['bold']))
    print('')
    print(colored('Баланс ' + str(coin1) + ': ' + str(bb1), 'green', attrs=['bold']))
    print(colored('Баланс ' + str(coin2) + ': ' + str(bb2), 'yellow', attrs=['bold']))
    print('')
    """
    print('Block 3')

    config = ConfigObj('config.ini', encoding='utf8')
    interval_info = config['interval-info']['f']
    hold_coin = float(config['hold-coin']['hold'])
    call_function = buycoin_counting() # Функция вернет кортеж из 3-х элементов
    th = call_function[0] # Берерм 0-й элемент из кортежа - список торговой истории
    print(f'{len(th)} - Записей в истории торгов')
    time.sleep(1)
    open_orders = client.get_open_orders(symbol=TICKER)
    open_orders_len = len(open_orders)
    time.sleep(1)
    cash_coin1 = float(client.get_asset_balance(asset=coin1)['free'])
    OrderRate = config['order_rate']['or']  # Количество монет (биткоина) каждого ордера
    print('Block 4')
    time.sleep(1)

    if len(th) > 0:  # P1 проверка 1
        print('P1 start')
        if th[0]["isBuyer"] == True:
            print('P2 start')
            cash_coin2 = float(client.get_asset_balance(asset=coin2)['free'])
            time.sleep(1)
            CurrentPrice = client.get_orderbook_ticker(symbol=TICKER)['bidPrice']
            print('cash2 ', cash_coin2)
            # j = float(cash_coin2) * float(CurrentPrice)
            print('P2 stop')
            if cash_coin2 >= coin2_minQty and cash_coin2 > hold_coin:  # P3
                print('P3 start')
                print('есть монеты продаем')
                func_sell()
                print('Функция Sell отработала')
                print('P3 stop')
            else:  # P4
                print('P4 start')
                func_buy2()
                print('P4 stop')
        elif th[0]['isBuyer'] == False and open_orders_len > 0:  # P5
            print('P5 start')
            print(colored('ОРДЕР SELL ИСПОЛНЕН', 'green', attrs=['bold']))
            print('')
            print(colored('ЗАПУСКАЕМ МОДУЛЬ ПЕРЕСТРОЕНИЯ ОРДЕРОВ', 'green', attrs=['bold']))
            print('Проверка отступа от BIDS')
            func_bids()
            print('P5 stop')
        elif th[0]['isBuyer'] == False and open_orders_len == 0:  # P6
            print('P6 start')
            print(colored('ОРДЕР SELL ИСПОЛНЕН', 'green', attrs=['bold']))
            print('')
            print(
                colored('ОТКРЫТЫХ BUY ОРДЕРОВ НЕТ, ЗАПУСК МОДУЛЯ УСТАНОВКИ ПЕРВЫХ ОРДЕРОВ', 'green', attrs=['bold']))
            func_buy1()
            print('P6 stop')

    elif open_orders_len < 1 and float(cash_coin1) >= float(OrderRate):  # P7
        print('P7 start')
        func_buy1()
        print('P7 stop')

    elif len(th) == 0:
        print('ВЫПОЛНЯЕМ ПРОВЕРКУ УРОВНЯ ОРДЕРОВ К BIDS')
        func_bids()

    else:
        print(colored('МОНИТОРИНГ', 'green', attrs=['bold']))
        print('')
        print(colored('Пара: ' + str(coin1) + ' - ' + str(coin2), 'blue', attrs=['bold']))
        print(' ')

    cycle += 1
    config = ConfigObj('config.ini', encoding='utf8')
    print(colored('LAST_STEP: ' + config['last_step']['ls'], 'blue', attrs=['bold']))
    print('Конец цикла')
    log_start()
    time.sleep(7)

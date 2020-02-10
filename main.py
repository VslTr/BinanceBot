# BINANCE
import time
from configparser import ConfigParser
from binance.client import Client
from termcolor import colored
import colorama

colorama.init()  # для отображения цвета в windows cmd
cfg = ConfigParser()
#config_file = "C:\ Users\ trogwar\ Dropbox\ My Folder\ Cod_ing\ PycharmProjects\ MyPoloniex_0001.2.1/config.ini"  # для linux
cfg.read('config.ini', encoding='utf8')  # читаем конфиг

key = cfg['API']['key']
secret = cfg['API']['secret']
api_key = key
api_secret = secret
client = Client(api_key, api_secret)

interval_1 = cfg['interval-info']['f']
interval_2 = cfg['interval-info2']['f2']

coin1 = cfg['PARA']['coin1']  # первая монета пары (BTC, ETH, USDT)
coin2 = cfg['CURRENCY']['coin2']  # вторая монета пары

cc1 = client.get_asset_balance(asset=coin1)  # выбираем доступный баланс первой монеты пары
cc2 = client.get_asset_balance(asset=coin2)  # выбираем доступный баланс второй монеты пары
TICKER = coin2 + coin1  # TIKER - пара
My_List = client.get_open_orders(symbol=TICKER)  # Список открытых ордеров
Sum_Orders = len(My_List)


print(colored('Пара: ' + str(coin1) + ' - ' + str(coin2), 'green', attrs=['bold']))
print(colored('Баланс ' + str(coin1) + ': ' + str(cc1['free']), 'blue', attrs=['bold']))
print(colored('Баланс ' + str(coin2) + ': ' + str(cc2['free']), 'blue', attrs=['bold']))
print(colored('К-во ордеров: ' + str(Sum_Orders), 'blue'))
print(' ')
print(colored('******************************************************************', 'green',  attrs=['bold']))
print(' ')

cycle = 0
while True:

    print('Block 1')
    print('F1')
    def funcSELL():
        print(colored('ЗАПУСК ПРОГРАММЫ ПРОДАЖИ', 'green', attrs=['bold']))
        Buy_price = 0  # Цена покупки
        Buy_volume = 0  # Обьем покупки
        volume1 = 0
        volume2 = 0
        average = 0  # Усреднение
        Trade_History = 0
        Trade_History = len(client.get_my_trades(symbol=TICKER))
        Sell_Percent = cfg['procent-pro']['p4']  # Процент продажи (профит)
        b = []
        s = []
        all_open_orders = client.get_open_orders()
        n = 0
        try:
            for j in all_open_orders:
                if all_open_orders[n]['side'] == 'BUY':
                    b.append(all_open_orders[n]['orderId'])
                elif all_open_orders[n]['side'] == 'SELL':
                    s.append(all_open_orders[n]['orderId'])
            n += 1

            print('BUY ', b)
            print('SELL ', s)

            len_s = len(s)
            if len_s != 0:
                cancel = client.cancel_order(symbol=TICKER, orderId=s[0]) 
                print('Предыдущий ордер на продажу закрыт !')
                print(cancel)
            else:
                print('Нет SELL ордеров')
        except Exception:
            print('')
        ###################################
        i = 0
        while i < Trade_History:
            # Пока i меньше количества ордеров в истории продолжаем считать, как i сравняется выходим из цыкла
            # (все покупки в истории посчитаны)
            TypeOrder = p.returnTradeHistory(currencyPair=TICKER)[i]['type']
            if TypeOrder == 'buy':
                Buy_price = p.returnTradeHistory(currencyPair=TICKER)[i]['rate']  # Запросили по какой ставке были покупки
                Buy_volume = p.returnTradeHistory(currencyPair=TICKER)[i]['amount']  # запросили сколько купили
                volume1 = volume1 + float(Buy_volume) * float(Buy_price)  # считаем объем монет (btc, usd) потраченных на покупку
                volume2 = volume2 + float(Buy_volume)  # польный объем купленных монет, плюсуем предыдущие покупки
                average = volume1 / volume2  # усредняем купленное
                i += 1  # добавляем к i 1, считаем дальше
            elif TypeOrder == 'sell':
                print('Buy ОРДЕРА ПОСЧИТАНЫ')
                break

        #percent = 0
        #PriceSellOrder = 0
        #cash_с = float(balance[coin2]['available'])
        cash_c = float(p.returnBalances()[coin2])
        percent = float(average) / 100.0 * float(SellPercent)  # считаем процент продажи
        print('процент продажи percent: ', percent)
        PriceSellOrder = float(average) + float(percent)  # считаем цену ордера продажи с учетом процента продажи
        print('цена ордера: ', PriceSellOrder)
        #SetSellOrder = p.sell(TICKER, PriceSellOrder, cash_c)
        SetSellOrder = p.sell(currencyPair=TICKER, rate=PriceSellOrder, amount=cash_c)
        # выставляем ордер на продажу, с параметрами: цена ордера и баланс (вся купленная крипта)
        print(colored('Добавлен SELL ордер: ' + str(SetSellOrder) + 'blue', attrs=['bold']))


    print('F2')
    def funcBUY1():
        OrderVol = cfg['order_rate']['or']  # ставка (кол. монет) ордера
        currentPrice = p.returnOrderBook(currencyPair=TICKER)['bids'][0][0]  # Узнаем текущую цену крайнего ордера на покупку
        StepUP = cfg['otstup-1']['p1']  # Отступ первого ордера в % от bids
        percent = float(currentPrice) / 100 * float(StepUP)  # Считаем процент отступа от bids
        OrderPrice = float(currentPrice) - float(percent)  # Считаем цену для ордера
        volume = float(OrderVol) / float(OrderPrice)
        # Считаем размер первого ордера покупки (на покупку скольки монет будем выставлять ордер)
        SetOrder = p.buy(currencyPair=TICKER, rate=OrderPrice, amount=volume)  # выставляем ордер с параметрами: цена, размер
        print('Создан первый ордер:', SetOrder)

        CfgBuyOrders = cfg['amount_orders']['am']  # Количество ордеров
        StepUP2 = cfg['otstup-2']['p2']
        mtg = cfg['martingale']['mr']  # Процент увеличения следующего ордера, Мартингейл
        i = 0
        LastOrderPrice= p.returnOpenOrders(currencyPair=TICKER)[0]['rate']  # Узнаем ставку последнего ордера
        TempOrderPrice = LastOrderPrice
        coinOrderSum = p.returnOpenOrders(currencyPair=TICKER)[0]['total']  # баланс (0-го, он всегда bay и самый крайний от bids) ордера в btc
        Coin1Volume = coinOrderSum
        print('1TempOrderPrice: ', TempOrderPrice, '1TempVolume: ', Coin1Volume)
        while i < int(CfgBuyOrders):
            # LastOrderRate = p.returnOpenOrders(TICKER)[0]['rate']  # Узнаем ставку последнего ордера
            SecondOrderPrice = float(TempOrderPrice) - float(TempOrderPrice) / 100 * float(StepUP2)
            # Ситаем цену следующего ордера
            print('SecondOrderPrice: ', SecondOrderPrice)
            TempOrderPrice = SecondOrderPrice
            print('TempOrderPrice: ', str(TempOrderPrice))  # Для проверки (после отладки можно удалить)
            SecondVolume = (float(Coin1Volume) + float(Coin1Volume) / 100 * float(mtg)) / float(SecondOrderPrice)  # Считаем размер следующего ордера
            print('SecondVolume: ', str(SecondVolume))
            Coin1Volume = float(SecondVolume) * float(TempOrderPrice)
            print('Coin1Volume: ', str(Coin1Volume))  # Для проверки (после отладки можно удалить)
            SetSecondOrder = p.buy(currencyPair=TICKER, rate=SecondOrderPrice, amount=SecondVolume)
            # выставляем следующий ордер с параметрами: цена, размер
            print('СОЗДАН ОРДЕР: ', SetSecondOrder)
            i += 1
            time.sleep(float(interval_info))
        time.sleep(float(interval_info))

    print('F3')
    def funcBUY2(): # функция высталяющая ниже ордера на покупку, при условии исполнения buy ордеров
        print('Start BUY2')
        OpenOrders = p.returnOpenOrders(currencyPair=TICKER)
        SumOrders = len(OpenOrders)
        if SumOrders == 0:
            print('Нет bay ордеров, переход к модулю установки первых ордеров')
            funcBUY1()
        else:
            AmountOrders = cfg['amount_orders']['am']  # Количество ордеров в конфиге
            step2 = cfg['otstup-2']['p2']  # Процент между ордерами
            mtg = cfg['martingale']['mr']  # Процент увеличения следующего ордера, Мартингейл

            i = 0
            buy_count = 0
            try:
                while i < SumOrders:
                    order = p.returnOpenOrders(currencyPair=TICKER)[i]['type']
                    if order == "buy":
                        buy_count += 1
                    else:
                        print('')
                    i += 1
                    time.sleep(0.2)
            except Exception:
                print('')
            print('Колличесвто открытых Buy ордеров: ', buy_count)

            THtype = p.returnTradeHistory(currencyPair=TICKER)[0]['type']
            if int(buy_count) < int(AmountOrders) and THtype == 'buy':
                print(colored('ОРДЕР НА ПОКУПКУ БЫЛ ИСПЛНЕН', 'green', attrs=['bold']))
                print(colored('ДОБАВЛЯЕМ ОРДЕРА','green', attrs=['bold']))

                #lastBay = p.returnTradeHistory(currencyPair=TICKER)[0]['rate']  # Ставка последнего ордера
                #print('lastBay ', lastBay)
                coinOrderSum = p.returnOpenOrders(currencyPair=TICKER)[0]['total']
                # баланс (0-го, он всегда bay и самый дальний от bids) ордера в btc
                # (на сколько btc или usd мы выставили ордеров)
                order_rate = p.returnOpenOrders(currencyPair=TICKER)[0]['rate']
                temp_orderrate = order_rate
                j = buy_count
                while j < int(AmountOrders):
                    OrderPrice = float(temp_orderrate) - float(temp_orderrate) / 100 * float(step2)  # Считаем цену нового ордера
                    print('OrderPrice ', OrderPrice)
                    OrderVol = (float(coinOrderSum) + float(coinOrderSum) / 100 * float(mtg)) / float(OrderPrice)  # Считаем обьем ордера
                    print('OrderVol ', OrderVol)
                    Coin1Vol = float(OrderVol) * float(OrderPrice)
                    print('Coin1Vol объем btc для след ордера: ', Coin1Vol)
                    cash_c2 = float(p.returnBalances()[coin1])
                    print('cash coin1 ',cash_c2)
                    if float(cash_c2) > float(Coin1Vol):
                        SetOrder = p.buy(currencyPair=TICKER, rate=OrderPrice, amount=OrderVol)  # Выставляем ордер
                        print('Добавленый ордер: ' + str(SetOrder))
                        temp_orderrate = OrderPrice  # ставка по которой выставили ордер
                    else:
                        print(colored('НЕДОСТАТОЧНО СРЕДСТВ ДЛЯ ДОБАВЛЕНИЯ ОРДЕРА' + ' !!!', 'red', attrs=['bold']))
                        break
                    j += 1
                    time.sleep(0.2)

    print('F4')
    def funcBIDS():
        OpenOrders = p.returnOpenOrders(currencyPair=TICKER) # Получаем список открытых ордеров
        SumOpenOrders = len(OpenOrders)
        #if int(SumOpenOrders) > 0:
        step1 = cfg['otstup-0']['p']  # Отступ первого ордера в % от bids
        step2 = cfg['otstup-2']['p2']  # Отступ первого ордера в % от bids
        cash = float(balance[coin1]['available'])
        TypeOpenOrders = p.returnOpenOrders(currencyPair=TICKER)[-1]['type']  # проверяем последний ордер (нет ли открытого sell)
        print('Установленно ' + str(SumOpenOrders) + ' ордера')
        CurrentPrice = p.returnOrderBook(currencyPair=TICKER)['bids'][0][0]  # Узнаем текущую цену (bids)
        percent = float(CurrentPrice) / 100 * float(step1)
        OrderPrice = float(CurrentPrice) - float(percent)  # Считаем цену для ордера с учетом процента
        print('OrderPrice ', OrderPrice)
        Order1 = p.returnOpenOrders(currencyPair=TICKER)[-1]['rate']  # Запрашиваем цену превого текущего ордера bay от bids
        print('Order1 ', Order1)
        if SumOpenOrders > 0 and TypeOpenOrders == 'buy' and float(OrderPrice) > float(Order1):
            print(colored('ПОДТЯГИВАЕМ ОРДЕРА К BIDS', 'blue', attrs=['bold']))
            j = 0
            while j < SumOpenOrders:
                try:
                    OrderN = p.returnOpenOrders(currencyPair=TICKER)[0]['orderNumber']
                    close = p.cancelOrder(orderNumber=OrderN)
                    print('Удален ордер N: ' + str(OrderN))
                except Exception:
                    print('')
                j += 1
                time.sleep(0.2)

            print(colored('ЗАПУСК МОДУЛЯ УСТАНОВКИ BUY ОРДЕРОВ', 'green', attrs=['bold']))
            funcBUY1()
            time.sleep(0.2)
        else:
            print('Параметры не соответствуют условиям проверки, funcBIDS NOT WORK')


    print('Block 2')
    print(colored('----------------------- ' + str(cycle) + ' -----------------------------', 'red', 'on_grey',
                  attrs=['bold']))
    print(' ')

    bb1 = p.returnBalances()[coin1]
    bb2 = p.returnBalances()[coin2]
    print(colored('Пара: ' + str(coin1) + ' - ' + str(coin2), 'blue', attrs=['bold']))
    print(' ')
    print(colored('Баланс ' + str(coin1) + ': ' + str(bb1), 'green', attrs=['bold']))
    print(colored('Баланс ' + str(coin2) + ': ' + str(bb2), 'yellow', attrs=['bold']))
    print(' ')
    print('Block 3')

    cash_1 = 0
    cash_2 = 0
    interval_info = cfg['interval-info']['f']
    TradeHistory = p.returnTradeHistory(currencyPair=TICKER)
    THLen = len(TradeHistory)
    print('THLen: ' + str(THLen))
    OpenOrders = p.returnOpenOrders(currencyPair=TICKER)
    OOLen = len(OpenOrders)
    cash_1 = float(p.returnBalances()[coin1])
    OrderRate = cfg['order_rate']['or']  # Количество монет (биткоина) каждого ордера
    print('Block 4')

    if THLen > 0:  # P1 проверка 1
        print('P1 start')
        THtype = p.returnTradeHistory(currencyPair=TICKER)[0]['type']
        print("Тип последнего ордера ", str(THtype))
        #try:
            #THtype = p.returnTradeHistory(TICKER)[0]['type']
        #except Exception:
            #print('Сработало исключение !!! стр.71')
        print('P1 stop')
        if THtype == 'buy':  # P2
            print('P2 start')
            # if THtype == 'buy' and float(cash_coin2) > 0.001:
            cash_2 = float(p.returnBalances()[coin2])
            CurrentPrice = p.returnOrderBook(currencyPair=TICKER)['bids'][0][0]
            print('cash2 ', cash_2)
            j = float(cash_2) * float(CurrentPrice)
            print('P2 stop')
            if float(cash_2) > 0 and j >= 0.0001:  # P3
                print('P3 start')
                print('есть монеты продаем')
                funcSELL()
                print('Функция Sell отработала')
                print('P3 stop')
            else:  # P4
                print('P4 start')
                print('Ничего не купили или ордер BUY исполнен не полностью')
                funcBUY2()
                print('P4 stop')
        elif THtype == 'sell' and OOLen > 0:  #P5
            print('P5 start')
            print(colored('ОРДЕР SELL ИСПОЛНЕН', 'green', attrs=['bold']))
            print('')
            print(colored('ЗАПУСКАЕМ МОДУЛЬ ПЕРЕСТРОЕНИЯ ОРДЕРОВ', 'green', attrs=['bold']))
            print('Проверка отступа от BIDS')
            funcBIDS()
            print('P5 stop')
        elif THtype == 'sell' and OOLen == 0:  # P6
            print('P6 start')
            print(colored('ОРДЕР SELL ИСПОЛНЕН', 'green', attrs=['bold']))
            print('')
            print(colored('ОТКРЫТЫХ BUY ОРДЕРОВ НЕТ, ЗАПУСК МОДУЛЯ УСТАНОВКИ ПЕРВЫХ ОРДЕРОВ', 'green', attrs=['bold']))
            funcBUY1()
            print('P6 stop')

    elif OOLen < 1 and float(cash_1) >= float(OrderRate):  # P7
        print('P7 start')
        funcBUY1()
        print('P7 stop')

    else:  # P8
        print('P8 start')
        print(colored('МОНИТОРИНГ', 'green', attrs=['bold']))
        print('')
        print(colored('Пара: ' + str(coin1) + ' - ' + str(coin2), 'blue', attrs=['bold']))
        print(' ')
        print('P8 stop')

    cycle += 1
    print('Конец цикла')
    time.sleep(3)




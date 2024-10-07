#работа с ордерами
#/route/{origin}/{destination}/ - прокладка маршрута
from predmet import proverka
from region_list import constellation_list
import requests

test = [{"duration":90,"is_buy_order":False,"issued":"2024-06-15T13:58:46Z","location_id":60003892,"min_volume":1,"order_id":6809583623,"price":751000.0,"range":"region","system_id":30001405,"type_id":380,"volume_remain":3,"volume_total":3},{"duration":90,"is_buy_order":False,"issued":"2024-03-28T11:59:11Z","location_id":60003841,"min_volume":1,"order_id":6747586568,"price":595.0,"range":"region","system_id":30001376,"type_id":380, "volume_remain":9508, "volume_total":24573}]

def get_spisok(reg, sell_buy): #фортирует общий список предметов в системе
    url = f'https://esi.evetech.net/latest/markets/{reg}/orders/'
    a = 0
    resp_out = []
    while True:
        a += 1
        resp_temp = get_api(url, str(a), sell_buy)
        if resp_temp == False:
            break
        print(a)
        for i in resp_temp:
            resp_out.append({'price': i['price'], 'system_id': i['system_id'], 'type_id': i['type_id'],
                             'volume_remain': i['volume_remain']})
    return resp_out

def get_api(url, params, buy_sell): #получение API с сайта
    headers = {'User-Agent': 'Chrome/39.0.2171.95 Safari/537.36'}
    try:
        par = {'page': params, 'order_type': buy_sell}
        response = requests.get(url, headers=headers, params=par, timeout=10)
        if response.ok == True:
            resp = response.json()
            return resp
        else:
            print(f'Проблемы с подключением {print(response)}')
            return False
    except requests.exceptions.Timeout:
        print("Timeout occurred")
        return 'Time out'
    except requests.exceptions.ConnectionError:
        print("No response")
    return False


def spisok(order_list = test, name = 'type_id'): #выбирает из ордеров уникальные номера
    spisok = []
    for i in order_list:
        spisok.append(i[name])
    return spisok

def tovar_price(order_list, type_id, naz): #выбирает все ордера на товар и добавляем комиссию
    tovar_out = []
    for order in order_list:
        if order['type_id'] == type_id:
            tovar_out.append({"volume_remain": order["volume_remain"], 'price': order["price"]*naz})
    return tovar_out

def tovar_price_out(order_list, type_id, naz): #выбирает все ордера на товар и добавляем комиссию
    tovar_out = []
    for order in order_list:
        if order['type_id'] == type_id:
            tovar_out.append({"volume_remain": order["volume_remain"], 'price': order["price"]*naz, 'station_id': order["station_id"]})
    return tovar_out

def spisok_tovarov_buy(resp_out, resp_in, sys_out, sys_in, naz): #на вход список ордеров двух систем номера систем и наценка на покупку
    list_out, list_in = [], []
    for order in resp_out:
        if order['system_id'] == int(sys_out):
            list_out.append(order)

    for order in resp_in:
        if int(order['system_id']) == int(sys_in):
            list_in.append(order)

    type_out = spisok(list_out, 'type_id') #номера товаров
    type_in = spisok(list_in, 'type_id') #номера товаров
    type_list = list(set(type_out) & set(type_in))
    type_list.sort()
    list_end = []
    for type_id in type_list:
        ob = proverka(type_id)['ob'] #получение объема предмета
        order_out = tovar_price_out(list_out, type_id, 1) #все ордера по товару на покупку
        order_in = tovar_price(list_in, type_id, naz) #все ордера по товару на покупку
        order_out.sort(key=lambda x: x.get('price'))
        order_in.sort(key=lambda x: x.get('price'), reverse=True)
        x , y = 0 , 0
        print('type_id')
        while order_out[x]['price'] < order_in[y]['price']:
            if order_out[x]["volume_remain"] < order_in[y]["volume_remain"]:
                profit = order_in[y]['price'] - order_out[x]['price']
                kub_price = (order_in[y]['price']-order_out[x]['price'])/ob
                list_end.append({'type_id': type_id, 'price_out': order_out[x]['price'], 'profit': profit, 'volume': order_out[x]["volume_remain"], 'kub_price': kub_price, 'ob' : ob })
                order_in[y]["volume_remain"] -= order_out[x]["volume_remain"]
                x += 1
            elif order_out[x]["volume_remain"] > order_in[y]["volume_remain"]:
                profit = order_in[y]['price'] - order_out[x]['price']
                kub_price = (order_in[y]['price'] - order_out[x]['price']) / ob
                list_end.append({'type_id': type_id, 'price_out': order_out[x]['price'], 'profit': profit, 'volume': order_in[y]["volume_remain"], 'kub_price': kub_price, 'ob' : ob })
                order_out[x]["volume_remain"] -= order_in[y]["volume_remain"]
                y += 1
            else:
                profit = order_in[y]['price'] - order_out[x]['price']
                kub_price = (order_in[y]['price'] - order_out[x]['price']) / ob
                list_end.append({'type_id': type_id, 'price_out': order_out[x]['price'], 'profit': profit, 'volume': order_in[y]["volume_remain"], 'kub_price': kub_price, 'ob' : ob })
                x += 1
                y += 1

            if x == len(order_out) or y == len(order_in): break

    return list_end

def get_resp(url): #получение API с сайта без параметров
    headers = {'User-Agent': 'Chrome/39.0.2171.95 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.ok == True:
            resp = response.json()
            return resp
        else:
            print(f'Проблемы с подключением {print(response)}')
            return False
    except requests.exceptions.Timeout:
        print("Timeout occurred")
    except requests.exceptions.ConnectionError:
        print("No response")
    return False

def track(sys_out, sys_in): #прокладывает путь между двумя системами
    url = f'https://esi.evetech.net/latest/route/{sys_out}/{sys_in}/'
    resp_out = get_resp(url)
    return resp_out

def region_list(): #использовал для создания списка регионов region_list.py
    url = 'https://evetycoon.com/api/v1/market/regions'
    reg_dic = get_resp(url)
    print(reg_dic)
    return reg_dic

def constellation_list_f(): #использовал для создания списка созвездий region_list.py
    url = 'https://esi.evetech.net/legacy/universe/constellations/'
    const_id_list = get_resp(url)
    const_list = []
    for id in const_id_list:
        url = f'https://esi.evetech.net/legacy/universe/constellations/{id}'
        const_list_tmp = get_resp(url)
        keys = ['constellation_id', 'region_id']
        const_list_tmp1 = {k: const_list_tmp.get(k, None) for k in keys}
        const_list.append(const_list_tmp1)
        print(id)
    print(const_list)
    return const_list

def system_list(): #использовал для создания списка систем region_list.py
    url = 'https://esi.evetech.net/dev/universe/systems/'
    system_id_list = get_resp(url)
    system_list = []
    for id in system_id_list:
        url = f'https://esi.evetech.net/dev/universe/systems/{id}'
        system_list_tmp = get_resp(url)
        keys = ['system_id', 'name']
        system_list_tmp1 = {k: system_list_tmp.get(k, None) for k in keys}
        for i in constellation_list:
            if i['constellation_id'] == system_list_tmp['constellation_id']:
                system_list_tmp1['region_id'] = i['region_id']
                break
        system_list.append(system_list_tmp1)
        print(id)
    print(system_list)
    return system_list

def system_info(sys): #информация по системе
    #входящее значение - число
    #пример результата
    #{'constellation_id': 20000209, 'name': 'Torrinos', 'planets': [{'planet_id': 40090878}, {'moons': [40090880], 'planet_id': 40090879}, {'moons': [40090882, 40090883, 40090884, 40090885, 40090886], 'planet_id': 40090881}, {'asteroid_belts': [40090888], 'moons': [40090889, 40090890, 40090891, 40090892, 40090893, 40090894, 40090895, 40090896, 40090897], 'planet_id': 40090887}, {'asteroid_belts': [40090903], 'moons': [40090899, 40090900, 40090901, 40090902, 40090904, 40090905, 40090906, 40090907, 40090908, 40090909, 40090910, 40090911, 40090912, 40090913, 40090914, 40090915, 40090916, 40090917, 40090918, 40090919, 40090920], 'planet_id': 40090898}, {'asteroid_belts': [40090922, 40090923, 40090924, 40090929], 'moons': [40090925, 40090926, 40090927, 40090928, 40090930, 40090931, 40090932, 40090933, 40090934, 40090935, 40090936, 40090937, 40090938, 40090939, 40090940, 40090941, 40090942, 40090943], 'planet_id': 40090921}, {'asteroid_belts': [40090946, 40090951, 40090954, 40090955, 40090957], 'moons': [40090945, 40090947, 40090948, 40090949, 40090950, 40090952, 40090953, 40090956, 40090958], 'planet_id': 40090944}, {'asteroid_belts': [40090965], 'moons': [40090960, 40090961, 40090962, 40090963, 40090964, 40090966], 'planet_id': 40090959}], 'position': {'x': -2.2741640581855194e+17, 'y': 1.0714092404522848e+17, 'z': 1.9936347925498147e+17}, 'security_class': 'C', 'security_status': 0.5196676850318909, 'star_id': 40090877, 'stargates': [50003515, 50003516], 'stations': [60000946, 60002326, 60004036, 60004042, 60004045, 60004201], 'system_id': 30001429}
    url = f'https://esi.evetech.net/dev/universe/systems/{sys}'
    system_id_list = get_resp(url)
    #print(system_id_list)
    return system_id_list

def constellation_info(con): #информация по созвездию
    #входящее значение - число
    #пример результата
    #{'constellation_id': 20000209, 'name': 'Asalola',
     #'position': {'x': -2.219338101965536e+17, 'y': 1.1361829249192586e+17, 'z': 1.851487694419098e+17},
     #'region_id': 10000016, 'systems': [30001424, 30001425, 30001426, 30001427, 30001428, 30001429]}

    url = f'https://esi.evetech.net/legacy/universe/constellations/{con}'
    const_id_list = get_resp(url)
    #print(const_id_list)
    return const_id_list

def station_info(station): #информация по станции
    #входящее значение - число
    #пример результата
    #{'solar_system_id': 30001429, 'station_name': 'Torrinos V - Moon 16 - Home Guard Logistic Support'}
    url = f'https://esi.evetech.net/legacy/universe/stations/{station}/'
    station_id_list = get_resp(url)
    #print(station_id_list)
    return station_id_list

def get_spisok_in(reg, sell_buy, station): #фортирует общий список предметов в системе куда летим
    url = f'https://esi.evetech.net/v1/markets/{reg}/orders/'
    a = 0
    resp_out = []
    while True:
        a += 1
        resp_temp = get_api(url, str(a), sell_buy)
        if resp_temp == False:
            break
        elif resp_temp == 'Time out':
            a -= 1
            continue
        print(a)
        for i in resp_temp:
            if i['location_id'] == station:
                resp_out.append([i['type_id'], i['price'], i['volume_remain']])
                #resp_out.append({'price': i['price'], 'type_id': i['type_id'],
                #                 'volume_remain': i['volume_remain']})
        resp_out.sort()
    return resp_out

def get_spisok_out(reg, sell_buy, station): #фортирует общий список предметов в системе
    url = f'https://esi.evetech.net/v1/markets/{reg}/orders/'
    a = 0
    resp_out = []
    while True:
        a += 1
        resp_temp = get_api(url, str(a), sell_buy)
        if resp_temp == False:
            break
        elif resp_temp == 'Time out':
            a -= 1
            continue
        print(a)
        for i in resp_temp:
            if i['location_id'] in station:
                resp_out.append([i['type_id'], i['price'], i['volume_remain'], i['location_id']])
                #resp_out.append({'price': i['price'], 'station_id': i['location_id'], 'type_id': i['type_id'],
                #                 'volume_remain': i['volume_remain']})
        resp_out.sort()
    return resp_out

def advansed_price():
    url = 'https://esi.evetech.net/latest/markets/prices/'
    return get_resp(url)

def get_spisok_in_reg(reg, sell_buy): #фортирует общий список предметов в системе
    url = f'https://esi.evetech.net/latest/markets/{reg}/orders/'
    a = 0
    resp_out = []
    while True:
        a += 1
        resp_temp = get_api(url, str(a), sell_buy)
        if resp_temp == False:
            break
        elif resp_temp == 'Time out':
            a -= 1
            continue
        print(a)
        for i in resp_temp:
                resp_out.append([i['type_id'], i['price'], i['volume_remain'], i['location_id']])
        resp_out.sort()
    return resp_out


if __name__ == '__main__':
    tmp = system_info(30000142)
    print(tmp['stations'])
    #tmp1 = constellation_info(20000209)
    tmp3 = station_info(60003760)

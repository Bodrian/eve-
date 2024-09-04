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
        response = requests.get(url, headers=headers, params=par, timeout=5)
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
    naz = naz #потери от налогов и комиссий
    list_end = []
    for type_id in type_list:
        ob = proverka(type_id)['ob'] #получение объема предмета
        order_out = tovar_price(list_out, type_id, 1) #все ордера по товару на покупку
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
        response = requests.get(url, headers=headers, timeout=5)
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

if __name__ == '__main__':
    system_list()

#нужно достать список всех станций на пути следования, помотреть sell ордера и сравнить их с житой, если список по профиту более 500тыс то заехать забрать

#так выглядит ордер
#{"duration":90,"is_buy_order":false,"issued":"2024-07-15T16:16:51Z","location_id":60003760,"min_volume":1,"order_id":6831996927,"price":39960000.0,"range":"region","system_id":30000142,"type_id":28264,"volume_remain":15,"volume_total":15}
#так выглядит описание системы
    #{"constellation_id":20000020,"name":"Jita","planets":[{"planet_id":40009077},{"planet_id":40009078},{"moons":[40009081],"planet_id":40009080},{"moons":[40009083,40009084,40009085,40009087,40009088,40009089,40009090,40009091,40009092,40009093,40009094,40009097],"planet_id":40009082},{"moons":[40009099,40009100,40009101,40009102,40009103,40009104,40009105,40009106,40009107,40009108,40009109,40009110,40009111,40009112,40009113,40009114,40009115],"planet_id":40009098},{"moons":[40009118],"planet_id":40009116},{"moons":[40009121,40009122],"planet_id":40009119},{"planet_id":40009123}],"position":{"x":-129064861735000000.0,"y":60755306910000000.0,"z":117469227060000000.0},"security_class":"B","security_status":0.9459131360054016,"star_id":40009076,"stargates":[50001248,50001249,50001250,50013876,50013913,50013921,50013928],"stations":[60000361,60000364,60000451,60000463,60002953,60002959,60003055,60003460,60003463,60003466,60003469,60003757,60003760,60004423,60015169],"system_id":30000142}

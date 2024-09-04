#расчеты
from predmet import proverka
temp = [{'name': 'Compact Explosive Shield Hardener', 'type_id': 9646, 'price_out': 28000.0, 'profit': 8827.599999999999, 'volume': 1, 'kub_price': 8827.599999999999}, {'name': 'Spatial Attunement Unit', 'type_id': 33195, 'price_out': 3789.0, 'profit': 2927.0, 'volume': 2, 'kub_price': 1463.5}, {'name': 'Dairy Products', 'type_id': 3717, 'price_out': 1.47, 'profit': 90.806, 'volume': 15, 'kub_price': 6.053733333333333}, {'name': 'Data Sheets', 'type_id': 3812, 'price_out': 141.0, 'profit': 15.519599999999997, 'volume': 7564, 'kub_price': 0.002051771549444738}, {'name': 'Data Sheets', 'type_id': 3812, 'price_out': 141.0, 'profit': 15.519599999999997, 'volume': 7564, 'kub_price': 0.002051771549444738}]

def volume_list(value_ship=7500, end_list=temp): #оставляем только то что в корабль помещается
    volume_list = []
    for order in end_list:
        if value_ship >= order['volume']*order['ob']:
            volume_list.append(order)
            value_ship -= order['volume']
            print(value_ship)
        else:
            order['volume'] = value_ship/order['ob']
            volume_list.append(order)
            break
    return volume_list

def summa(list, key): #сумма объектов списка по ключу
    sum = 0
    for i in list:
        sum += i[key]
        print(sum)
    return sum

def print_res(list): #печать списка для покупок
    print('----------------')
    for i in list:
        print(f"{proverka(i['type_id'])['name']} - {i['volume']}шт. - {i['price_out']}$ - проф {int(i['profit'])}$ - проф за куб {int(i['kub_price'])} - объем {int(i['ob'])}")
    print('----------------')

if __name__ == '__main__':
    print(volume_list())
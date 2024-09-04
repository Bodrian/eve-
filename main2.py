# https://esi.evetech.net/latest/markets/groups/1857/ группа минералов
# https://www.adam4eve.eu/info_locations.php - список регионов
# https://esi.evetech.net/latest/markets/10000016/orders/
# https://www.adam4eve.eu/info_locations.php - список локаций (название систем)
# /v1/market/regions - возвращает список регинов с именами
# /v1/market/groups - возвращает список рыночных групп
# /v1/market/groups/{groupId}/types - возвращает список товаров
import requests
import datetime
import json
import time
from predmet import add_info
from order import spisok_tovarov_buy, get_spisok
from matem import volume_list, summa, print_res

if __name__ == '__main__':
    start_time = datetime.datetime.now() #замеряю время работы

    #volume_ship = input('введите объем грузового отсека')
    volume_ship = 7500

    #reg_out = input('введи регион отправления')
    reg_out = '10000002' #(the forge) jita
    #reg_out = '10000016' #Lonetrek
    #reg_out = '10000033' #The Cafidral
    #reg_out = '10000032'  # Sinq Laison
    #reg_out = '10000069' #Black Rise



    #sys_out = input('введи систему отправления')
    sys_out = '30000142' #jita - ok
    #sys_out = '30011407' #school - ok
    #sys_out = '30001363'  # Sobaseki Lonetrek - ok
    #sys_out = '30001395'  # Ylandoki Lonetrek 2
    #sys_out = '30001397' #Iiseras 3
    #sys_out = '30001396' #Aakari 3 - сжималка руды
    #sys_out = '30001394' #Korama 3
    #sys_out = '30001391' #Piekura 4
    #sys_out = '30001393' #Malkalen
    #sys_out = '30002780' #Muvolainen the kafidral 1
    #sys_out = '30002659'  # Dodixis Sinq Laison 15
    #sys_out = '30001376'  # Nourvukainen lanetrek 3 10% speed buur
    #sys_out = '30045324' #Onnamon BackRise
    #sys_out = '30001409'  # Umokka Lonetrak
    #sys_out = '30001429'  # Torrinos Lonetrak
    #sys_out = '30001428' #Ibura Lonetrak
    #sys_out = '30001426' #Isinoka Lonetrak
    #sys_out = '30001427' #Yoma lonetrak
    #sys_out = '30001425' #Oipo lonetrak
    #sys_out = '30001424' #Haajinin lonetrak
    #sys_out = '30001401' #Nonni lonetrak

    #reg_in = input('введи регион прибытия')
    reg_in = '10000016' #Lonetrek
    #reg_in = '10000002' #(the forge)jita
    #reg_in = '10000032' #Sinq Laison

    #sys_in = input('введите систему прибытия')
    #sys_in = '30011407' #school
    #sys_in = '30000142' #jita
    #sys_in = '30001363' #Sobaseki Lonetrek
    #sys_in = '30001395' #Ylandoki Lonetrek 2
    #sys_in = '30001376' #Nourvukainen lanetrek 3 10% speed buur
    #sys_in = '30002659' #Dodixis Sinq Laison 15
    #sys_in = '30001409' #Umokka Lonetrak
    #sys_in = '30001405' # Kakakela Lonetrak
    #sys_in = '30001408' #Ruvas Lonetrak
    sys_in = '30001429'  # Torrinos Lonetrak
    #sys_in = '30001424' #Haajinin lonetrak


    resp_out = get_spisok(reg_out, 'sell')
    resp_in = get_spisok(reg_in, 'buy')

    with open("resp_in.py", "w") as file:
        file.write(f'resp_in = {resp_in}')
    with open("resp_out.py", "w") as file:
        file.write(f'resp_out = {resp_out}')

    naz = 0.935 # наценка на транзакцию
    list_end = spisok_tovarov_buy(resp_out, resp_in, sys_out, sys_in, naz) # получаем список покупок
    print(list_end)
    list_end.sort(key=lambda x: x.get('kub_price'), reverse=True) #сортируем список по профиту за куб
    print(list_end)
    #list_end = volume_list(volume_ship, list_end) #оставляем в списке отлько то что влезает в карабль
    print(list_end)
    #profit = summa(list_end, 'profit') #считаем профит
    #volume = summa(list_end, 'volume')*summa(list_end, 'ob') #считаем объем
    #list_end.sort(key=lambda x: x.get('type_id')) #сортируем по имени чтобы дубли находились рядом
    print_res(list_end) #печатаем результат в нормальном формате

    #print(f'Система: {sys_in}, Профит: {int(profit)} $, Объем: {int(volume)} м.куб.')



    add_info() #обновляет базу предметов - всегда запусать вконце
    finish_time = datetime.datetime.now() #замеряю время работы
    print('Время работы: ' + str(finish_time - start_time))

    # end_list = []
    # prof1 = 0
    # for order_out in list_out:
    #     naz = 1.1
    #     price = order_out['price'] * naz
    #     for order_in in list_in:
    #         if order_in['type_id'] == order_out['type_id']:
    #             if order_in['price'] > price:
    #                 name = predmet_info(order_out["type_id"])['name']
    #                 if order_in["volume_remain"] >= order_out["volume_remain"]:
    #                     prof = int(order_out["volume_remain"] * (order_in["price"]*0.92 - order_out["price"]))
    #                     if prof > 5000: #если профит меньше 10000 - то нафиг
    #                         print(f'{name} - {order_out["price"]}$ - {order_out["volume_remain"]}шт. - профит: {prof} $- {order_in["price"]}$')
    #                         end_list.append({'type_name': name, 'price': order_out["price"], 'value': order_out["volume_remain"], 'profit': prof})
    #                         prof1 += prof
    #                         break
    #                 else:
    #                     prof = int(order_in["volume_remain"]*(order_in["price"]*0.92 - order_out["price"]))
    #                     if prof > 5000:  # если профит меньше 10000 - то нафиг
    #                         print(f'{name} - {order_out["price"]}$ - {order_in["volume_remain"]}шт. - профит: {prof} $ - {order_in["price"]}$' )
    #                         end_list.append({'type_name': name, 'price': order_out["price"], 'value': order_in["volume_remain"], 'profit': prof})
    #                         order_out["volume_remain"] = order_out["volume_remain"] - order_in["volume_remain"]
    #                         prof1 += prof
    # print(prof1)
    #
    # #print(doc_in)
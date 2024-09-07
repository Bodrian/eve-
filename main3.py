#программа собирает ордера только с региона вылета - другие регионы не участвуют
import datetime
from order import track, system_info, constellation_info, get_spisok_in, get_spisok_out, advansed_price
from resp_in import resp_in
from resp_out import resp_out
from matem import print_res

if __name__ == '__main__':
    sys_out = 30001429 #система из которой вылетаем
    sys_in = 30000142 #система куда прилетаем
    station_in = 60003760 #станция куда прилетаем
    reg_in = 10000002 #регион куда летим
    naz = 0.935  # наценка на транзакцию
    koef = 0.5 #коэффициент жадности
    station_list = []
    start_time = datetime.datetime.now()  # замеряю время работы

    track_list = track(sys_out, sys_in) #выводит номера систем между точками назначения - список []
    print('номера систем по пути', track_list)
    track_list.pop(-1)
    print('номера систем по пути', track_list)
    region_out = constellation_info(system_info(sys_out)['constellation_id'])['region_id'] #определяем регион вылета - далее тут нужно докуртить, чтобы собирало все регионы по ходу движения
    print('регион вылета', region_out)
    #ниже процедура для вывода списка станций которые пролетаем
    for sys in track_list:
        station = system_info(sys).get('stations')
        print(station)
        if station != None:
            station_list += station
    print('список станций', station_list)

    #resp_in = get_spisok_in(reg_in, 'buy', station_in) #список ордеров на продажу
    #with open("resp_in.py", "w") as file:
    #    file.write(f'resp_in = {resp_in}')

    #resp_out = get_spisok_out(region_out, 'sell', station_list)
    #with open("resp_out.py", "w") as file:
    #    file.write(f'resp_out = {resp_out}')

    avarage_price = advansed_price() # получаем список средних цен
    print(avarage_price)
    for order in resp_out:
        for ava_price in avarage_price:
            if order['type_id'] == ava_price['type_id']:
                if ava_price.get('average_price') != None:
                    if order['price']/koef < ava_price['average_price']:
                        print(order)
                break



    finish_time = datetime.datetime.now()  # замеряю время работы
    print('Время работы: ' + str(finish_time - start_time))
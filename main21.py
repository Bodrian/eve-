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
    #
    # track_list = track(sys_out, sys_in) #выводит номера систем между точками назначения - список []
    # print('номера систем по пути', track_list)
    # track_list.pop(-1)
    # print('номера систем по пути', track_list)
    # region_out = constellation_info(system_info(sys_out)['constellation_id'])['region_id'] #определяем регион вылета - далее тут нужно докуртить, чтобы собирало все регионы по ходу движения
    # print('регион вылета', region_out)
    # #ниже процедура для вывода списка станций которые пролетаем
    # for sys in track_list:
    #     station = system_info(sys).get('stations')
    #     print(station)
    #     if station != None:
    #         station_list += station
    # print('список станций', station_list)

    # resp_in = get_spisok_in(reg_in, 'buy', station_in) #список ордеров на продажу [type, price, volume]
    # with open("resp_in.py", "w") as file:
    #     file.write(f'resp_in = {resp_in}')
    #
    # resp_out = get_spisok_out(region_out, 'sell', station_list)
    # with open("resp_out.py", "w") as file:
    #     file.write(f'resp_out = {resp_out}')

    resp_in_s = resp_in
    resp_out_s = resp_out

    while resp_in_s != []:
        # -------- получаем список ордеров на покупку отсортировано от меньшего к большему-------
        type_list_in = []
        type_id = resp_in_s[0][0]
        if resp_in_s[0][0] != resp_in_s[1][0]:
            type_list_in.append(resp_in_s.pop(0))
        else:
            while resp_in_s[0][0] == resp_in_s[1][0]:
                type_list_in.append(resp_in_s.pop(0))
            type_list_in.append(resp_in_s.pop(0))
        type_list_in.reverse()
        # ------------------------------------------------

        # --------- получаем список товаров на продажу с этим же номером ------
        type_list_out = []
        while int(resp_out_s[0][0]) <= type_id:
            if resp_out_s[0][0] < type_id:
                resp_out_s.pop(0)
            else:
                type_list_out.append(resp_out_s.pop(0))
            if resp_out_s == []: break
        if resp_out_s == []: break
        # ----------------------------
        if type_list_out != [] and type_list_out[0][1] < type_list_in[0][1]*naz: # работаю только с товарами которые где-то можно купить
            type_list_out_buy = []
            for order in type_list_out:
                if  order[1] < type_list_in[0][1]*naz: type_list_out_buy.append(order)
            print(type_list_in)
            print(type_list_out_buy)
        # -------- выбираем товар для покупки
        # --- формируем список покупок
        


    finish_time = datetime.datetime.now()  # замеряю время работы
    print('Время работы: ' + str(finish_time - start_time))
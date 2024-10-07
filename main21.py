#программа собирает ордера на покупку с маршрута от точки вылета до хаба
# https://esi.evetech.net/latest/universe/stations/{station_id}/ инфа по станции
import datetime
from order import station_info, track, system_info, constellation_info, get_spisok_in, get_spisok_out, advansed_price
from resp_in import resp_in
from resp_out import resp_out
from predmet import proverka
from matem import print_res

if __name__ == '__main__':
    price_kub = 50 #указать минимальный профит с куба
    prof_lim = 100000 #лимит по профиту - если меньше этого лимита, то на станцию не летим
    sys_out = 30001429 #система из которой вылетаем
    sys_in = 30000142 #система куда прилетаем
    station_in = 60003760 #станция куда прилетаем
    reg_in = 10000002 #регион куда летим
    naz = 0.935  # наценка на транзакцию
    station_list = []
    start_time = datetime.datetime.now()  # замеряю время работы

    track_list = track(sys_out, sys_in) #выводит номера систем между точками назначения - список []
    track_list.pop(-1) #удаляем систему прибытия
    # print('номера систем по пути', track_list)
    region_out = constellation_info(system_info(sys_out)['constellation_id'])['region_id'] #определяем регион вылета - далее тут нужно докуртить, чтобы собирало все регионы по ходу движения
    # print('регион вылета', region_out)

    #ниже процедура для вывода списка станций, которые пролетаем
    for sys in track_list:
        station = system_info(sys).get('stations')
        #print(station)
        if station != None:
            station_list += station
    #station_list = [60000946, 60002326, 60004036, 60004042, 60004045, 60004201, 60004204, 60004336, 60000949, 60003988, 60004192, 60004195, 60002320, 60003985, 60004198, 60004339, 60004345, 60000940, 60000943, 60002317, 60002323, 60003982, 60004039, 60004207, 60004342, 60000265, 60000313, 60000316, 60000736, 60000739, 60000979, 60001522, 60002914, 60003742, 60003865, 60000256, 60000271, 60000310, 60002305, 60004003, 60007372, 60007375, 60000733, 60002920, 60002923, 60003124, 60003877, 60006844, 60007369, 60000352, 60004027, 60004291, 60004294, 60013105, 60001462, 60001468, 60004432, 60007597, 60000763, 60000844, 60000892, 60000895, 60002419, 60003094, 60003916, 60003925, 60004012, 60004018]
    #print('список станций', station_list)
    resp_in = get_spisok_in(reg_in, 'buy', station_in) #список ордеров на продажу [type, price, volume]
    #with open("resp_in.py", "w") as file:
    #    file.write(f'resp_in = {resp_in}')
    #
    resp_out = get_spisok_out(region_out, 'sell', station_list)
    #with open("resp_out.py", "w") as file:
    #    file.write(f'resp_out = {resp_out}')

    resp_in_s = resp_in
    resp_out_s = resp_out
    final_list_out_buy = []
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
            #print(type_list_in)
            #print(type_list_out_buy)
            # ранее мы отобрали товары по ценам, сейчас отберем по количеству
            i, j = 0, 0
            while i <= (len(type_list_in) - 1) and j <= (len(type_list_out_buy) - 1):
                if type_list_in[i][2] <= 0: i+=1
                elif type_list_out_buy[j][2] <= 0: j+=1
                elif type_list_out_buy[j][1] >= (type_list_in[i][1] * naz): break
                elif type_list_out_buy[j][2] == type_list_in[i][2]:            #если количество на покупку и продажу равно
                    type_list_out_buy[j].append((type_list_in[i][1] * naz) - type_list_out_buy[j][1])
                    final_list_out_buy.append(type_list_out_buy[j])
                    type_list_in[i][2] = 0
                    type_list_out_buy[j][2] = 0
                    j += 1
                    i += 1
                elif type_list_out_buy[j][2] < type_list_in[i][2]:  #если количество на покупку меньше чем на продажу
                    type_list_out_buy[j].append((type_list_in[i][1] * naz) - type_list_out_buy[j][1])
                    final_list_out_buy.append(type_list_out_buy[j])
                    type_list_in[i][2] -= type_list_out_buy[j][2]
                    j +=1
                elif type_list_out_buy[j][2] > type_list_in[i][2]: #если количество на продажу больше чем на покупку
                    type_list_in[i].append(type_list_out_buy[j][3])
                    type_list_in[i].append((type_list_in[i][1] * naz) - type_list_out_buy[j][1])
                    final_list_out_buy.append(type_list_in[i])
                    type_list_out_buy[j][2] -= type_list_in[i][2]
                    i+=1
    #print(final_list_out_buy) #печатаем выгодные по цене ордера на покупку
    #print(len(final_list_out_buy))
    #проверяем, что все товары есть в списке товаров
    final1_list_out_buy = []
    for i in final_list_out_buy: #заменяем индекс товара на название и добавляем объем и убираем что не прошло по объему [имя, цена, количество, станция, проофит за штуку, объем)
        k = proverka(i[0])
        i[0] = k['name']
        i.append(k['ob'])
        if i[4] / i[5] > price_kub: final1_list_out_buy.append(i)
    print(final1_list_out_buy)
    print(len(final1_list_out_buy))
    #выводим список для каждой станции



    buy_dic = {}
    for i in station_list:
        prof = 0
        ob = 0
        spisok1 = []
        #print('номер станции', i)
        for j in final1_list_out_buy:
            if i == j[3]:
                spisok1.append(j[0]+' ' + str(j[2]))
                prof += j[4]*j[2]
                ob += j[5]*j[2]
        if prof > prof_lim:
            name_st = station_info(i)['station_name']
            buy_dic[name_st] = [spisok1, prof, ob]
    #print(buy_dic)
    #печатаем словарь в нормальном формате
    for station in buy_dic:
        print(station)
        for i in buy_dic[station][0]:
            print(i)
        print(f'Профит: {int(buy_dic[station][1])}, Объем: {buy_dic[station][2]}')
        print()




    # далее отсекаем ордера которые не подходят по объему




        # -------- выбираем товар для покупки

        # --- формируем список покупок
        


    finish_time = datetime.datetime.now()  # замеряю время работы
    print('Время работы: ' + str(finish_time - start_time))
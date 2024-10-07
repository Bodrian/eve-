#программа определяет куда лететь из Хаба (где больше всего ордеров на покупку)
import datetime
from order import get_spisok_in_reg, station_info, track, system_info, constellation_info, get_spisok_in, get_spisok_out, advansed_price
from resp_in import resp_in
from resp_out import resp_out
from predmet import proverka
from matem import print_res

if __name__ == '__main__':
    start_time = datetime.datetime.now()  # замеряю время работы
    price_kub = 50  # указать минимальный профит с куба
    prof_lim = 100000  # лимит по профиту - если меньше этого лимита, то на станцию не летим
    sys_out = 30000142 # система из которой вылетаем 30001429 торринос
    station_out = 60003760 #станция откуда летим жита
    #sys_in = 30000142  # система куда прилетаем 30000142 жита
    #station_in = 60003760  # станция куда прилетаем
    reg_in = 10000016  # регион куда летим
    reg_out = 10000002 #регион откуда летим
    naz = 0.935  # наценка на транзакцию

    resp_out = get_spisok_in(reg_out, 'sell', station_out)  # список ордеров на продажу [type, price, volume]
    with open("resp_out.py", "w") as file:
       file.write(f'resp_out = {resp_out}')
    #
    resp_in = get_spisok_in_reg(reg_in, 'buy')
    with open("resp_in.py", "w") as file:
       file.write(f'resp_in = {resp_in}')

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
        if type_list_out != [] and type_list_out[0][1] < type_list_in[0][
            1] * naz:  # работаю только с товарами которые где-то можно купить
            type_list_out_buy = []
            for order in type_list_out:
                if order[1] < type_list_in[0][1] * naz: type_list_out_buy.append(order)
            # print(type_list_in)
            # print(type_list_out_buy)
            # ранее мы отобрали товары по ценам, сейчас отберем по количеству
            i, j = 0, 0
            while i <= (len(type_list_in) - 1) and j <= (len(type_list_out_buy) - 1):
                if type_list_in[i][2] <= 0:
                    i += 1
                elif type_list_out_buy[j][2] <= 0:
                    j += 1
                elif type_list_out_buy[j][1] >= (type_list_in[i][1] * naz):
                    break
                elif type_list_out_buy[j][2] == type_list_in[i][2]:  # если количество на покупку и продажу равно
                    type_list_out_buy[j].append((type_list_in[i][1] * naz) - type_list_out_buy[j][1])
                    final_list_out_buy.append(type_list_in[i])
                    type_list_in[i][2] = 0
                    type_list_out_buy[j][2] = 0
                    j += 1
                    i += 1
                elif type_list_out_buy[j][2] < type_list_in[i][2]:  # если количество на покупку меньше чем на продажу
                    type_list_out_buy[j].append(type_list_in[i][3])
                    type_list_out_buy[j].append((type_list_in[i][1] * naz) - type_list_out_buy[j][1])
                    final_list_out_buy.append(type_list_out_buy[j])
                    type_list_in[i][2] -= type_list_out_buy[j][2]
                    j += 1
                elif type_list_out_buy[j][2] > type_list_in[i][2]:  # если количество на продажу больше чем на покупку
                    #type_list_in[i].append(type_list_in[i][3])
                    type_list_in[i].append((type_list_in[i][1] * naz) - type_list_out_buy[j][1])
                    final_list_out_buy.append(type_list_in[i])
                    type_list_out_buy[j][2] -= type_list_in[i][2]
                    i += 1
    print(final_list_out_buy) #печатаем выгодные по цене ордера на покупку
    print(len(final_list_out_buy))

    # проверяем, что все товары есть в списке товаров
    final1_list_out_buy = []
    for i in final_list_out_buy:  # заменяем индекс товара на название и добавляем объем и убираем что не прошло по объему [имя, цена, количество, станция, проофит за штуку, объем)
        k = proverka(i[0])
        i[0] = k['name']
        i.append(k['ob'])
        if len(i) != 6: continue
        if i[4] / i[5] > price_kub: final1_list_out_buy.append(i)
    # print(final1_list_out_buy)
    # print(len(final1_list_out_buy))
    # выводим список для каждой станции

    #составляем список станций
    station_list = []
    for k in final1_list_out_buy:
        station_list.append(k[3])
    station_list = list(set(station_list))

    buy_dic = {}
    for i in station_list:
        prof = 0
        ob = 0
        spisok1 = []
        # print('номер станции', i)
        for j in final1_list_out_buy:
            if i == j[3]:
                spisok1.append(j[0] + ' ' + str(j[2]))
                prof += j[4] * j[2]
                ob += j[5] * j[2]
        if prof > prof_lim:
            if i > 70000000: continue
            name_st = station_info(i)['station_name'] + ' ' + str(i)
            buy_dic[name_st] = [spisok1, prof, ob]
    # print(buy_dic)
    # печатаем словарь в нормальном формате
    for station in buy_dic:
        print(station)
        for i in buy_dic[station][0]:
            print(i)
        print(f'Профит: {int(buy_dic[station][1])}, Объем: {buy_dic[station][2]}')
        print()

    finish_time = datetime.datetime.now()  # замеряю время работы
    print('Время работы: ' + str(finish_time - start_time))

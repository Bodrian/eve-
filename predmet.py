import requests
import json
from predmet_list import predmet_list

def get_predmet(url): #получение API с сайта
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

def predmet_info(type_id='1333'): #как будет выглядеть в справочнике товар
    url = f'https://esi.evetech.net/latest/universe/types/{type_id}/'
    predmet = get_predmet(url)
    if predmet['volume'] == 0: predmet['volume'] = 0.01
    return {"type_id" : int(type_id), 'name' : predmet['name'], 'ob' : predmet['volume']}

def proverka(type_id = 1333): #наличие товара в базе - если нет - заносим в кэш и получаем имя
    for i in predmet_list:
        if i['type_id'] == type_id:
            res = {'name': i['name'], 'ob': i['ob']}
            return res

    temp = predmet_info(type_id)
    predmet_list.append(temp)
    res = {'name':temp['name'], 'ob': temp['ob']}
    print(res)
    return res

def add_info(predmet_list=predmet_list):
    with open("predmet_list.py", "w") as file:
        file.write(f'predmet_list = {predmet_list}')
    print(f'Словарь перезаписан')

if __name__ == '__main__':
    proverka(1333)
    proverka(1335)
    proverka(52590)
    proverka(1335)
    add_info()




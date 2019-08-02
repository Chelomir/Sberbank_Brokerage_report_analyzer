# Регулярные выражения в Питоне
# https://habr.com/ru/post/349860/
import re
import json
import requests
from bs4 import BeautifulSoup

# TODO: Эти переменные используются и в main.py и в scrap.py - Надо оставить в одном месте
# Используемые типы активов
BONDS = 'ОБЛИГАЦИИ'
SHARES = 'АКЦИИ'
GOLD = 'ЗОЛОТО'
CASH = 'CASH'

# структура соответствия кодов типов активов
ACTIVE_TYPES = {
    'Облигация федерального займа': BONDS,
    'Инвестиционный пай иностранного эмитента': GOLD, # ETF у меня только на золото)
    'Акция обыкновенная': SHARES,
    'Акция иностранного эмитента': SHARES,
    'Облигация': BONDS,
    'ГДР': SHARES,
    'Акция привилегированная': SHARES
}

def get_info(path):
    '''Получаем массив данных из HTML-файла, расположенного по пути path   '''
    reading_a = False
    # Портфель Ценных Бумаг
    pcb = []
    reading_pcb = False
    # Справочник Ценных Бумаг
    scb = []
    reading_scb = False
    
    file = open(path,'r',encoding="utf-8")

    try:
        for line in file:
            # Определяем, что подошли к концу отчёта
            if line.find("Подпись") != -1:
                end_of_report = True

            if line.find("Оценка активов") != -1:
                reading_a = True
            if line.find("Портфель Ценных Бумаг") != -1:
                reading_pcb = True
            if line.find("Справочник Ценных Бумаг") != -1:
                reading_scb = True

            # читаем Оценка активов для определение объёма денежных и стоимости портфеля (для фондового рынка, т.к. срочным не занимаюсь)
            if reading_a:
                # определяем конец таблицы
                if line.find(r"/table") != -1:
                    reading_a = False
                # из строчки Фондовый рынок берём данные        
                if line.find(r'Фондовый рынок') != -1:
                    temp_arr = re.split(r"</td>",line)
                    #my_portfel['Оценка портфеля ЦБ, руб'] = float(re.split(r">",temp_arr[1])[1].replace(' ',''))
                    #my_portfel['Денежные средства, руб.'] = float(re.split(r">",temp_arr[2])[1].replace(' ',''))
                    #my_portfel['Оценка, руб'] = float(re.split(r">",temp_arr[3])[1].replace(' ',''))
                    # !!!!!!!!!!!!
                    pcb.append(
                            {
                                'Тип': CASH,
                                'Рыночная стоимость': float(re.split(r">",temp_arr[2])[1].replace(' ','')),
                                'ISIN ценной бумаги': None,
                                'Наименование': 'Денежные средства, руб.'
                            }
                        )
                    
            # читаем Портфель Ценных Бумаг для создания справочника имеющихся ЦБ. 
            if reading_pcb:
                # определяем конец таблицы
                if line.find(r"/table") != -1:
                    reading_pcb = False
                # каждую строчку таблицы преобразуем в объект my_cb и добавляем к массиву pcb
                if line.find(r'4px') != -1:
                    # ценная бумага из строчки
                    my_cb = {}
                    # TODO: Когда-нибудь попробовать создать регулярное выражение, которое сразу будет выдавать массив значений (без необходимости двойного split'а)
                    temp_arr = re.split(r"</td>",line)
                    my_cb['Наименование'] = re.split(r">",temp_arr[0])[1]
                    my_cb['ISIN ценной бумаги'] = re.split(r">",temp_arr[1])[1]
                    # my_cb['Валюта рыночной цены'] = re.split(r">",temp_arr[2])[1]
                    # my_cb['Начало периода: Количество, шт'] = re.split(r">",temp_arr[3])[1]
                    # my_cb['Начало периода: Номинал'] = re.split(r">",temp_arr[4])[1]
                    # my_cb['Начало периода: Рыночная цена'] = re.split(r">",temp_arr[5])[1]
                    # my_cb['Начало периода: Рыночная стоимость, без НКД'] = re.split(r">",temp_arr[6])[1]
                    # my_cb['Начало периода: НКД'] = re.split(r">",temp_arr[7])[1]
                    # my_cb['Конец периода: Количество, шт'] = re.split(r">",temp_arr[8])[1]
                    # my_cb['Конец периода: Номинал'] = re.split(r">",temp_arr[9])[1]
                    # my_cb['Конец периода: Рыночная цена'] = re.split(r">",temp_arr[10])[1]
                    #### my_cb['Конец периода: Рыночная стоимость, без НКД'] = float(re.split(r">",temp_arr[11])[1].replace(' ',''))
                    my_cb['Рыночная стоимость'] = float(re.split(r">",temp_arr[11])[1].replace(' ',''))
                    # my_cb['Конец периода: НКД'] = re.split(r">",temp_arr[12])[1]
                    # my_cb['Изменение за период: Количество, шт'] = re.split(r">",temp_arr[13])[1]
                    # my_cb['Изменение за период: Рыночная стоимость'] = re.split(r">",temp_arr[14])[1]
                    # my_cb['Плановые показатели: Плановые зачисления по сделкам, шт'] = re.split(r">",temp_arr[15])[1]
                    # my_cb['Плановые показатели: Плановые списания по сделкам, шт'] = re.split(r">",temp_arr[16])[1]
                    # my_cb['Плановые показатели: Плановый исходящий остаток, шт'] = re.split(r">",temp_arr[17])[1]
                    pcb.append(my_cb)

            # читаем Справочник Ценных Бумаг для определения типа актива. В дальнейшем, на его основе, проставим в справочнике имеющихся ЦБ проставим признак типа актива
            if reading_scb:
                # определяем конец таблицы
                if line.find(r"/table") != -1:
                    reading_scb = False
                # каждую строчку таблицы преобразуем в объект cb и добавляем к массиву scb
                if line.find(r'4px') != -1:
                    # ценная бумага из строчки
                    cb = {}
                    # TODO: Когда-нибудь попробовать создать регулярное выражение, которое сразу будет выдавать массив значений (без необходимости двойного split'а)
                    temp_arr = re.split(r"</td>",line)
                    # cb['Наименование'] = re.split(r">",temp_arr[0])[1]
                    cb['Код'] = re.split(r">",temp_arr[1])[1]
                    cb['ISIN ценной бумаги'] = re.split(r">",temp_arr[2])[1]
                    # cb['Эмитент'] = re.split(r">",temp_arr[3])[1]
                    cb['Вид, Категория, Тип, иная информация'] = re.split(r">",temp_arr[4])[1]
                    # cb['Выпуск, Транш, Серия'] = re.split(r">",temp_arr[5])[1]
                    scb.append(cb)
    except UnicodeDecodeError:
        if end_of_report == False:
            print("!!!Ошибка чтения (может негативно влиять на результат)")
    file.close()

    '''
    Пытаемся прочитать сектора из файла. Если файла нет, то пишем его с данных из smart-lab.ru
    '''
    try:
        with open('codes.json', 'r', encoding='utf-8') as json_data_file:
            codes = json.load(json_data_file)
    except FileNotFoundError:
        soup = BeautifulSoup(requests.get(r'https://smart-lab.ru/forum/sectors/').text,'html.parser')
        sector_blocks = soup.findAll('div', {'class': "kompanii_sector"})
        codes = {}
        for sector_block in sector_blocks:
            sector_name = sector_block.find('h2').text
            codes_urls = sector_block.findAll('li')
            for code_url in codes_urls:
                code = code_url.find('a')['href'][7:]
                codes[code] = sector_name
        with open('codes.json', 'w', encoding='utf-8') as f:
            json.dump(codes, f, ensure_ascii=False, indent=4)

    # здесь мы имеем 2 заполненных массива
    # - pcb - содержит объекты-ценные бумаги которые есть в нашем портфеле, со стоимостью и количеством
    # - scb - содержит объекты-ценные бумаги с описанием их типа (Облигация, акция и пр.)
    # Скрестить эти два массива мы можем по атрибуту *ISIN ценной бумаги*
    # Заодно проставляем сектора
    for cb in pcb:
        for b in scb:
            if cb['ISIN ценной бумаги'] == b['ISIN ценной бумаги']:
                cb['Тип'] = ACTIVE_TYPES[b['Вид, Категория, Тип, иная информация']]
                cb['Код'] = b['Код']
                if (cb['Тип'] == SHARES):
                    try:
                        sector = codes[cb['Код']]
                    except:
                        try:
                            # Вероятно код от префа, т.е. для проверки надо убрать последнюю P
                            temp_code = cb['Код'][:4]
                            sector = codes[temp_code]
                        except:                         
                            sector = "НЕ ОПОЗНАН"
                    cb['Сектор'] = sector

    return pcb
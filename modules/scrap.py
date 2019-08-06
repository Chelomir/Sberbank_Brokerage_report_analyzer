# Регулярные выражения в Питоне
# https://habr.com/ru/post/349860/
import re
import json
import requests
from bs4 import BeautifulSoup

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
    # Портфель Ценных Бумаг
    pcb = []
    # Справочник Ценных Бумаг
    scb = []
    with open(path, 'r',encoding="utf-8", errors = "ignore") as file:
        bs = BeautifulSoup(file.read(), 'html.parser')
        # Таблица Оценка активов
        table_ocenka_activov = bs.find(string = re.compile("Оценка активов")).parent.findNext('table')
        cash = float(table_ocenka_activov.find('td', string = re.compile("Фондовый рынок")).nextSibling.nextSibling.text.replace(' ',''))
        pcb.append(
                {
                    'Тип': CASH,
                    'Рыночная стоимость': cash,
                    'ISIN ценной бумаги': None,
                    'Наименование': 'Денежные средства, руб.'
                }
            )
        # Таблица Портфель Ценных Бумаг
        table_portfel_cennyh_bumag = bs.find(string = re.compile("Портфель Ценных Бумаг")).parent.findNext('table')
        cbs = table_portfel_cennyh_bumag.findAll('td',{'style':"font-size='4px';"})
        for cb in cbs:
            my_cb = {}
            my_cb['Наименование'] = cb.text
            cb_cells = cb.findNextSiblings()
            my_cb['ISIN ценной бумаги'] = cb_cells[0].text
            # my_cb['Валюта рыночной цены'] = cb_cells[1].text
            # my_cb['Начало периода: Количество, шт'] = cb_cells[2].text
            # my_cb['Начало периода: Номинал'] = cb_cells[3].text
            # my_cb['Начало периода: Рыночная цена'] = cb_cells[4].text
            # my_cb['Начало периода: Рыночная стоимость, без НКД'] = cb_cells[5].text
            # my_cb['Начало периода: НКД'] = cb_cells[6].text
            # my_cb['Конец периода: Количество, шт'] = cb_cells[7].text
            # my_cb['Конец периода: Номинал'] = cb_cells[8].text
            # my_cb['Конец периода: Рыночная цена'] = cb_cells[9].text
            #### my_cb['Конец периода: Рыночная стоимость, без НКД'] = cb_cells[10].text
            my_cb['Рыночная стоимость'] = float(cb_cells[10].text.replace(' ',''))
            # my_cb['Конец периода: НКД'] = cb_cells[11].text
            # my_cb['Изменение за период: Количество, шт'] = cb_cells[12].text
            # my_cb['Изменение за период: Рыночная стоимость'] = cb_cells[13].text
            # my_cb['Плановые показатели: Плановые зачисления по сделкам, шт'] = cb_cells[14].text
            # my_cb['Плановые показатели: Плановые списания по сделкам, шт'] = cb_cells[15].text
            # my_cb['Плановые показатели: Плановый исходящий остаток, шт'] = cb_cells[16].text
            pcb.append(my_cb)

        # Таблица Справочник Ценных Бумаг
        table_spravochnik_cennyh_bumag = bs.find(string = re.compile("Справочник Ценных Бумаг")).parent.findNext('table')
        sbs = table_spravochnik_cennyh_bumag.findAll('td',{'style':"font-size='4px';"})
        for sb in sbs:
            cb = {}
            # cb['Наименование'] = sb.text
            sb_cells = sb.findNextSiblings()
            cb['Код'] = sb_cells[0].text
            cb['ISIN ценной бумаги'] = sb_cells[1].text
            # cb['Эмитент'] = sb_cells[2].text
            cb['Вид, Категория, Тип, иная информация'] = sb_cells[3].text
            cb['Выпуск, Транш, Серия'] = sb_cells[4].text
            scb.append(cb)


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

    '''
    здесь мы имеем 2 заполненных массива
    - pcb - содержит объекты-ценные бумаги которые есть в нашем портфеле, со стоимостью и количеством
    - scb - содержит объекты-ценные бумаги с описанием их типа (Облигация, акция и пр.)
    Скрестить эти два массива мы можем по атрибуту *ISIN ценной бумаги*
    Заодно проставляем сектора
    '''
    for cb in pcb:
        for b in scb:
            if cb['ISIN ценной бумаги'] == b['ISIN ценной бумаги']:
                cb['Тип'] = ACTIVE_TYPES[b['Вид, Категория, Тип, иная информация']]
                cb['Код'] = b['Код']
                cb['Выпуск, Транш, Серия'] = b['Выпуск, Транш, Серия']
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
                if (cb['Тип'] == BONDS):
                    # TODO: Сделать заполнение на основе атрибута 'Выпуск, Транш, Серия'
                    '''
                    Примеры значений атрибута 'Выпуск, Транш, Серия'
                    24019RMFS - ОФЗ
                    RU35018KAR0 - Субъект
                    4B02-03-36324-R - Корпорат
                    '''
                    if re.match(r'\d\d\d\d\dRMFS',b['Выпуск, Транш, Серия']):
                        cb['Сектор'] = "ОФЗ"
                    else:
                        if re.match(r'RU\d\d\d\d\d\D\D\D\d',b['Выпуск, Транш, Серия']):
                            cb['Сектор'] = "Субъект"
                        else:
                            cb['Сектор'] = "Корпорат"
    return pcb
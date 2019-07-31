# Регулярные выражения в Питоне
# https://habr.com/ru/post/349860/
import re

# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.product.html#pandas.DataFrame.product
import pandas as pd

# Путь к файлу с брокерским отчётом
REPORT_PATH = r"C:\Users\User\Desktop\brokercode_030719_030719_D.html"
file = open(REPORT_PATH,'r',encoding="utf-8")

# Используемые типы активов
BONDS = 'ОБЛИГАЦИИ'
SHARES = 'АКЦИИ'
GOLD = 'ЗОЛОТО'
CASH = 'CASH'

# Целевые параметры портфеля
ideal_portfel = {
    BONDS: 40,
    GOLD: 10,
    SHARES: 50,
    CASH: 0
}

reading_a = False
# Портфель Ценных Бумаг
pcb = []
reading_pcb = False
# Справочник Ценных Бумаг
scb = []
reading_scb = False

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
                            'Конец периода: Рыночная стоимость, без НКД': float(re.split(r">",temp_arr[2])[1].replace(' ','')),
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
                my_cb['Конец периода: Рыночная стоимость, без НКД'] = float(re.split(r">",temp_arr[11])[1].replace(' ',''))
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
                # cb['Код'] = re.split(r">",temp_arr[1])[1]
                cb['ISIN ценной бумаги'] = re.split(r">",temp_arr[2])[1]
                # cb['Эмитент'] = re.split(r">",temp_arr[3])[1]
                cb['Вид, Категория, Тип, иная информация'] = re.split(r">",temp_arr[4])[1]
                # cb['Выпуск, Транш, Серия'] = re.split(r">",temp_arr[5])[1]
                scb.append(cb)
except UnicodeDecodeError:
    if end_of_report == False:
        print("!!!Ошибка чтения (может негативно влиять на результат)")
file.close()

# здесь мы имеем 2 заполненных массива
# - pcb - содержит объекты-ценные бумаги которые есть в нашем портфеле, со стоимостью и количеством
# - scb - содержит объекты-ценные бумаги с описанием их типа (Облигация, акция и пр.)
# Скрестить эти два массива мы можем по атрибуту *ISIN ценной бумаги*

for cb in pcb:
    for b in scb:
        if cb['ISIN ценной бумаги'] == b['ISIN ценной бумаги']:
            cb['Тип'] = ACTIVE_TYPES[b['Вид, Категория, Тип, иная информация']]

# Получаем датафрейм для дальнейшей работы
df_pcb = pd.DataFrame(pcb)

# Полная стоимость портфеля
full_portfel_cost = round(df_pcb.agg({'Конец периода: Рыночная стоимость, без НКД' : ['sum']}).to_numpy()[0][0],2)

# Загруженные данные
#print(df_pcb.head())

# Сортируем по стоимости акций в портфеле
#print(df_pcb.sort_values(by=['Конец периода: Рыночная стоимость, без НКД'],ascending=False).head())

# Суммы, сгруппированные по типам актива
df_grouped_and_aggregated_pcb = df_pcb.groupby(["Тип"]).agg({'Конец периода: Рыночная стоимость, без НКД' : ['sum']})

# Вынимаем объект dict_portfel, содержащий стоимости типов актива в портфеле
for val in df_grouped_and_aggregated_pcb.to_dict().values():
    dict_portfel = val

#print(dict_portfel)

# additional_money = float(input("Введите сумму, которую собираемся доложить на счёт, рублей: "))
additional_money = 0
full_portfel_cost = full_portfel_cost + additional_money
dict_portfel[CASH] = dict_portfel[CASH] + additional_money

#print(dict_portfel)

# Доли активов в настоящее время (с учётом докладываемой суммы)
current_portions = {
    BONDS: round(dict_portfel[BONDS]*100/full_portfel_cost,2),
    SHARES: round(dict_portfel[SHARES]*100/full_portfel_cost,2),
    GOLD: round(dict_portfel[GOLD]*100/full_portfel_cost,2)
}

# Необходимые изменения в рублях для достижения идеальных пропорций
diff_portions = {
    BONDS: round((ideal_portfel[BONDS] - current_portions[BONDS])*full_portfel_cost/100,2),
    SHARES: round((ideal_portfel[SHARES] - current_portions[SHARES])*full_portfel_cost/100,2),
    GOLD: round((ideal_portfel[GOLD] - current_portions[GOLD])*full_portfel_cost/100,2)
}


# Вывод в консоль
print("-------------------------------------------------")
print("** Параметры портфеля в настоящее время (с учётом докладываемой суммы) **")
print(f"- Стоимость ценных бумаг:    {(full_portfel_cost - dict_portfel[CASH]):11} рублей")
print(f"- Денежные средства:         {dict_portfel[CASH]:11} рублей")
print(f"- Полная стоимость портфеля: {full_portfel_cost:11} рублей")
print("-------------------------------------------------")
print("** Доли активов в настоящее время (с учётом докладываемой суммы) **")
print(f"- Облигации, %:          {current_portions[BONDS]:5}")
print(f"- Акции, %:              {current_portions[SHARES]:5}")
print(f"- Золото, %:             {current_portions[GOLD]:5}")
print(f"- Денежные средства, %:  {round(dict_portfel[CASH]*100/full_portfel_cost,2):5}")
print("-------------------------------------------------")
print("** Необходимые изменения для достижения идеальных пропорций **")
if diff_portions[BONDS]>0:
    print(f"- Облигации:    купить на {diff_portions[BONDS]:11} рублей")
else:
    print(f"- Облигации:    продать на {abs(diff_portions[BONDS]):11} рублей")
if diff_portions[SHARES]>0:
    print(f"- Акции:        купить на {diff_portions[SHARES]:11} рублей")
else:
    print(f"- Акции:        продать на {abs(diff_portions[SHARES]):11} рублей")
if diff_portions[GOLD]>0:
    print(f"- Золото:       купить на {diff_portions[GOLD]:11} рублей")
else:
    print(f"- Золото:       продать на {abs(diff_portions[GOLD]):11} рублей")


"""
# Вывод в Jupyter Notebook
from IPython.display import HTML, display

html1 = ("<h2 style='padding: 8px'>Параметры портфеля в настоящее время (с учётом докладываемой суммы)</h2>"
         "<table class='table table-striped'>"
         "<thead> <tr> <th>Параметр</th> <th>Значение</th></tr> </thead>"
         "<tbody>"
         "<tr> <th scope='row'>Стоимость ценных бумаг, руб.</th> <td>"+ str(my_portfel['Оценка портфеля ЦБ, руб']) + "</td> </tr>"
         "<tr> <th scope='row'>Денежные средства, руб.</th> <td>"+ str(my_portfel['Денежные средства, руб.']) + "</td> </tr>"
         "<tr> <th scope='row'>Полная стоимость портфеля, руб.</th> <td>"+ str(my_portfel['Оценка, руб']) + "</td> </tr>"
         "</tbody> </table>")
html2 = ("<h2 style='padding: 8px'>Анализ типов активов (с учётом докладываемой суммы)</h2>"
          "<table class='table table-striped'>"
          "<thead> <tr> <th>Актив</th> <th>Текущая доля, %</th><th>Идеальная доля, %</th><th>Разница, руб</th></tr> </thead>"
          "<tbody>"
          "<tr> <th scope='row'>Облигации</th> <td>"+ str(current_portions[BONDS]) + "</td> <td>"+ str(ideal_portfel[BONDS]) + "</td> <td>"+ str(diff_portions[BONDS]) + "</td> </tr>"
          "<tr> <th scope='row'>Акции</th> <td>"+ str(current_portions[SHARES]) + "</td> <td>"+ str(ideal_portfel[SHARES]) + "</td> <td>"+ str(diff_portions[SHARES]) + "</td> </tr>"
          "<tr> <th scope='row'>Золото</th> <td>"+ str(current_portions[GOLD]) + "</td> <td>"+ str(ideal_portfel[GOLD]) + "</td> <td>"+ str(diff_portions[GOLD]) + "</td> </tr>"
          "<tr> <th scope='row'>Денежные средства</th> <td>"+ str(round(my_portfel['Денежные средства, руб.']*100/my_portfel['Оценка, руб'],2)) + "</td> </tr>"
          "</tbody> </table>")
display(HTML(html1))
display(HTML(html2))
"""
'''
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

#init_notebook_mode(connected=True)
'''
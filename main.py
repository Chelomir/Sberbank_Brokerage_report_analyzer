# https://devpractice.ru/python-lesson-18-annotations/
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.product.html#pandas.DataFrame.product
import pandas as pd

from modules import scrap

# Целевые параметры портфеля
ideal_portfel = {
    scrap.BONDS: 41,
    scrap.GOLD: 10,
    scrap.SHARES: 49,
    scrap.CASH: 0
}

# Путь к файлу с брокерским отчётом
REPORT_PATH = r"C:\Users\User\Desktop\brokercode_030719_030719_D.html"

pcb = scrap.get_info(REPORT_PATH)

# Получаем датафрейм для дальнейшей работы
df_pcb = pd.DataFrame(pcb)

# Полная стоимость портфеля
full_portfel_cost = round(df_pcb.agg({'Рыночная стоимость' : ['sum']}).to_numpy()[0][0],2)

df_pcb['% от полной стоимости портфеля'] = df_pcb['Рыночная стоимость']*100/full_portfel_cost

# Суммы, сгруппированные по типам актива
df_grouped_and_aggregated_pcb = df_pcb.groupby(["Тип"]).agg({'Рыночная стоимость' : ['sum']})

# Вынимаем объект dict_portfel, содержащий стоимости типов актива в портфеле
for val in df_grouped_and_aggregated_pcb.to_dict().values():
    dict_portfel = val

# Создаём датафрейм с одними акциями и сортируем по стоимости
df_pcb_shares = df_pcb[df_pcb['Тип'] == scrap.SHARES].sort_values(by=['Рыночная стоимость'],ascending=False)
df_pcb_shares['% от стоимости всех акций'] = df_pcb['Рыночная стоимость']*100/dict_portfel[scrap.SHARES]

# Суммы акций, сгруппированные по секторам
df_otrasl_grouped_and_aggregated_pcb = df_pcb_shares.groupby(["Сектор"]).agg({'Рыночная стоимость' : ['sum']})
# Сортируем
# TODO: Попытаться разобраться как работает строчка сортировки ниже (нашёл опытным путём, основа - stack())
df_otrasl_grouped_and_aggregated_pcb = df_otrasl_grouped_and_aggregated_pcb.stack().sort_values(by=['Рыночная стоимость'],ascending=False)
# TODO: Убрать sum
# Добавляем столбец - % от стоимости всех секторов = стомость_сектора/стоимость_всех_акций
df_otrasl_grouped_and_aggregated_pcb['% от стоимости всех акций'] = df_otrasl_grouped_and_aggregated_pcb['Рыночная стоимость']*100/dict_portfel[scrap.SHARES]

# Создаём датафрейм с одними облигациями и сортируем по стоимости
df_pcb_bonds = df_pcb[df_pcb['Тип'] == scrap.BONDS].sort_values(by=['Рыночная стоимость'],ascending=False)
df_pcb_bonds['% от стоимости всех облигаций'] = df_pcb['Рыночная стоимость']*100/dict_portfel[scrap.BONDS]

# Суммы облигаций, сгруппированные по типу ОФЗ, Субъект или Корпорат
df_tip_grouped_and_aggregated_pcb = df_pcb_bonds.groupby(["Сектор"]).agg({'Рыночная стоимость' : ['sum']})
# Сортируем
# TODO: Попытаться разобраться как работает строчка сортировки ниже (нашёл опытным путём, основа - stack())
df_tip_grouped_and_aggregated_pcb = df_tip_grouped_and_aggregated_pcb.stack().sort_values(by=['Рыночная стоимость'],ascending=False)
# TODO: Убрать sum
# Добавляем столбец - % от стоимости всех облигаций = стомость_типа/стоимость_всех_облигаций
df_tip_grouped_and_aggregated_pcb['% от стоимости всех облигаций'] = df_tip_grouped_and_aggregated_pcb['Рыночная стоимость']*100/dict_portfel[scrap.BONDS]

# additional_money = float(input("Введите сумму, которую собираемся доложить на счёт, рублей: "))
additional_money = 0
full_portfel_cost = full_portfel_cost + additional_money
dict_portfel[scrap.CASH] = dict_portfel[scrap.CASH] + additional_money

# Доли активов в настоящее время (с учётом докладываемой суммы)
current_portions = {
    scrap.BONDS: round(dict_portfel[scrap.BONDS]*100/full_portfel_cost,2),
    scrap.SHARES: round(dict_portfel[scrap.SHARES]*100/full_portfel_cost,2),
    scrap.GOLD: round(dict_portfel[scrap.GOLD]*100/full_portfel_cost,2),
    scrap.CASH: round(dict_portfel[scrap.CASH]*100/full_portfel_cost,2)
}

# Необходимые изменения в рублях для достижения идеальных пропорций
diff_portions = {
    scrap.BONDS: round((ideal_portfel[scrap.BONDS] - current_portions[scrap.BONDS])*full_portfel_cost/100,2),
    scrap.SHARES: round((ideal_portfel[scrap.SHARES] - current_portions[scrap.SHARES])*full_portfel_cost/100,2),
    scrap.GOLD: round((ideal_portfel[scrap.GOLD] - current_portions[scrap.GOLD])*full_portfel_cost/100,2)
}

#region Вывод в Jupyter Notebook
"""
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
          "<tr> <th scope='row'>Облигации</th> <td>"+ str(current_portions[scrap.BONDS]) + "</td> <td>"+ str(ideal_portfel[scrap.BONDS]) + "</td> <td>"+ str(diff_portions[scrap.BONDS]) + "</td> </tr>"
          "<tr> <th scope='row'>Акции</th> <td>"+ str(current_portions[scrap.SHARES]) + "</td> <td>"+ str(ideal_portfel[scrap.SHARES]) + "</td> <td>"+ str(diff_portions[scrap.SHARES]) + "</td> </tr>"
          "<tr> <th scope='row'>Золото</th> <td>"+ str(current_portions[scrap.GOLD]) + "</td> <td>"+ str(ideal_portfel[scrap.GOLD]) + "</td> <td>"+ str(diff_portions[scrap.GOLD]) + "</td> </tr>"
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
#endregion

# Заполняем Markdown-файл с описанием портфеля
with open ('portfel_result.md', 'w', encoding='utf-8') as portfel_result:
    # Параметры портфеля
    portfel_result.write('## Параметры портфеля\n')
    portfel_result.write(f"|Параметр|Значение|\n")
    portfel_result.write(f"|---|--:|\n")
    portfel_result.write(f"|Стоимость ценных бумаг, руб|{round(full_portfel_cost - dict_portfel[scrap.CASH],2)}|\n")
    portfel_result.write(f"|Денежные средства, руб|{dict_portfel[scrap.CASH]}|\n")
    portfel_result.write(f"|Полная стоимость портфеля, руб|{full_portfel_cost}|\n")

    # Доли активов
    portfel_result.write('## Доли активов\n')
    portfel_result.write(f"|Тип актива|Сумма|Доля от портфеля, %|Идеальная доля от портфеля, %|\n")
    portfel_result.write(f"|---|--:|--:|--:|\n")
    portfel_result.write(f"|Облигации|{round(dict_portfel[scrap.BONDS],2)}|{current_portions[scrap.BONDS]}|{ideal_portfel[scrap.BONDS]}|\n")
    portfel_result.write(f"|Акции|{dict_portfel[scrap.SHARES]}|{current_portions[scrap.SHARES]}|{ideal_portfel[scrap.SHARES]}|\n")
    portfel_result.write(f"|Золото|{dict_portfel[scrap.GOLD]}|{current_portions[scrap.GOLD]}|{ideal_portfel[scrap.GOLD]}|\n")
    portfel_result.write(f"|Денежные средства|{dict_portfel[scrap.CASH]}|{current_portions[scrap.CASH]}|{ideal_portfel[scrap.CASH]}|\n")

    # Необходимые изменения для достижения идеальных пропорций
    portfel_result.write('## Необходимые изменения для достижения идеальных пропорций\n')
    emoji_up = ':small_red_triangle:'
    emoji_down = ':small_red_triangle_down:'
    portfel_result.write(f"|Тип актива|{emoji_up}Купить/{emoji_down}Продать, руб|\n")
    portfel_result.write(f"|---|--:|\n")
    ## Облигации
    emoji_BONDS = emoji_up
    if diff_portions[scrap.BONDS]<0:
        emoji_BONDS = emoji_down
    portfel_result.write(f"|Облигации|{emoji_BONDS}{abs(diff_portions[scrap.BONDS])}|\n")
    ## Акции
    emoji_SHARES = emoji_up
    if diff_portions[scrap.SHARES]<0:
        emoji_SHARES = emoji_down
    portfel_result.write(f"|Акции|{emoji_SHARES}{abs(diff_portions[scrap.SHARES])}|\n")
    ## Золото
    emoji_GOLD = emoji_up
    if diff_portions[scrap.GOLD]<0:
        emoji_GOLD = emoji_down
    portfel_result.write(f"|Золото|{emoji_GOLD}{abs(diff_portions[scrap.GOLD])}|\n")

    # Акции в портфеле, отсортированные по стоимости
    portfel_result.write('# Акции\n')
    portfel_result.write('## Акции в портфеле, отсортированные по стоимости\n')
    portfel_result.write(f"|Код|Наименование|Рыночная стоимость|Сектор|% от полной стоимости портфеля|% от стоимости всех акций|\n")
    portfel_result.write(f"|---|---|---|---|--:|--:|\n")
    for index, row in df_pcb_shares.iterrows():
        portfel_result.write(f"|{row['Код']}|{row['Наименование']}|{row['Рыночная стоимость']}|{row['Сектор']}|{round(row['% от полной стоимости портфеля'],2)}|{round(row['% от стоимости всех акций'],2)}|\n")

    # Сектора в портфеле акций, отсортированные по стоимости
    portfel_result.write('## Сектора в портфеле акций, отсортированные по стоимости\n')
    portfel_result.write(f"|Сектор|Рыночная стоимость|% от стоимости всех акций|\n")
    portfel_result.write(f"|---|--:|--:|\n")
    for index, row in df_otrasl_grouped_and_aggregated_pcb.iterrows():
        portfel_result.write(f"|{index[0]}|{row['Рыночная стоимость']}|{round(row['% от стоимости всех акций'],2)}|\n")

    # Облигации в портфеле, отсортированные по стоимости
    portfel_result.write('# Облигации\n')
    portfel_result.write('## Облигации в портфеле, отсортированные по стоимости\n')
    portfel_result.write(f"|Наименование|Тип|Рыночная стоимость|% от полной стоимости портфеля|% от стоимости всех облигаций|\n")
    portfel_result.write(f"|---|---|--:|--:|--:|\n")
    for index, row in df_pcb_bonds.iterrows():
        portfel_result.write(f"|{row['Наименование']}|{row['Сектор']}|{row['Рыночная стоимость']}|{round(row['% от полной стоимости портфеля'],2)}|{round(row['% от стоимости всех облигаций'],2)}|\n")

    # Типы в портфеле облигаций, отсортированные по стоимости
    portfel_result.write('## Типы в портфеле облигаций, отсортированные по стоимости\n')
    portfel_result.write(f"|Тип|Рыночная стоимость|% от стоимости всех облигаций|\n")
    portfel_result.write(f"|---|--:|--:|\n")
    for index, row in df_tip_grouped_and_aggregated_pcb.iterrows():
        portfel_result.write(f"|{index[0]}|{round(row['Рыночная стоимость'],2)}|{round(row['% от стоимости всех облигаций'],2)}|\n")
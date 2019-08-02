# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.product.html#pandas.DataFrame.product
import pandas as pd

from modules import scrap

# TODO: Эти переменные используются и в main.py и в scrap.py - Надо оставить в одном месте
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
df_pcb_shares = df_pcb[df_pcb['Тип'] == SHARES].sort_values(by=['Рыночная стоимость'],ascending=False)
df_pcb_shares['% от стоимости всех акций'] = df_pcb['Рыночная стоимость']*100/dict_portfel[SHARES]
#print(df_pcb_shares.head(50))

# Суммы, сгруппированные по секторам
df_otrasl_grouped_and_aggregated_pcb = df_pcb_shares.groupby(["Сектор"]).agg({'Рыночная стоимость' : ['sum']})
#print(df_otrasl_grouped_and_aggregated_pcb)
# Сортируем
# TODO: Попытаться разобраться как работает строчка сортировки ниже (нашёл опытным путём, основа - stack())
df_otrasl_grouped_and_aggregated_pcb = df_otrasl_grouped_and_aggregated_pcb.stack().sort_values(by=['Рыночная стоимость'],ascending=False)
# TODO: Убрать sum
#print(df_otrasl_grouped_and_aggregated_pcb)
# Добавляем столбец - % от стоимости всех секторов = стомость_сектора/стоимость_всех_акций
df_otrasl_grouped_and_aggregated_pcb['% от стоимости всех секторов'] = df_otrasl_grouped_and_aggregated_pcb['Рыночная стоимость']*100/dict_portfel[SHARES]
print(df_otrasl_grouped_and_aggregated_pcb)

# additional_money = float(input("Введите сумму, которую собираемся доложить на счёт, рублей: "))
additional_money = 0
full_portfel_cost = full_portfel_cost + additional_money
dict_portfel[CASH] = dict_portfel[CASH] + additional_money

#print(dict_portfel)

# Доли активов в настоящее время (с учётом докладываемой суммы)
current_portions = {
    BONDS: round(dict_portfel[BONDS]*100/full_portfel_cost,2),
    SHARES: round(dict_portfel[SHARES]*100/full_portfel_cost,2),
    GOLD: round(dict_portfel[GOLD]*100/full_portfel_cost,2),
    CASH: round(dict_portfel[CASH]*100/full_portfel_cost,2)
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
print(f"- Денежные средства, %:  {current_portions[CASH]:5}")
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
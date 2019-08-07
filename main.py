# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.product.html#pandas.DataFrame.product
import pandas as pd

from modules import scrap

# Целевые параметры портфеля
ideal_portfel = {
    scrap.BONDS: 40,
    scrap.GOLD: 10,
    scrap.SHARES: 50,
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
print("-------------------------------------------------")
print("** TOP 5 Акции в портфеле, отсортированные по стоимости **")
print(df_pcb_shares[['Код','Наименование','Рыночная стоимость','Сектор','% от полной стоимости портфеля','% от стоимости всех акций']].head(5))

# Суммы акций, сгруппированные по секторам
df_otrasl_grouped_and_aggregated_pcb = df_pcb_shares.groupby(["Сектор"]).agg({'Рыночная стоимость' : ['sum']})
# Сортируем
# TODO: Попытаться разобраться как работает строчка сортировки ниже (нашёл опытным путём, основа - stack())
df_otrasl_grouped_and_aggregated_pcb = df_otrasl_grouped_and_aggregated_pcb.stack().sort_values(by=['Рыночная стоимость'],ascending=False)
# TODO: Убрать sum
# Добавляем столбец - % от стоимости всех секторов = стомость_сектора/стоимость_всех_акций
df_otrasl_grouped_and_aggregated_pcb['% от стоимости всех акций'] = df_otrasl_grouped_and_aggregated_pcb['Рыночная стоимость']*100/dict_portfel[scrap.SHARES]
print("-------------------------------------------------")
print("** Сектора в портфеле акций, отсортированные по стоимости **")
print(df_otrasl_grouped_and_aggregated_pcb)

# Создаём датафрейм с одними облигациями и сортируем по стоимости
df_pcb_bonds = df_pcb[df_pcb['Тип'] == scrap.BONDS].sort_values(by=['Рыночная стоимость'],ascending=False)
df_pcb_bonds['% от стоимости всех облигаций'] = df_pcb['Рыночная стоимость']*100/dict_portfel[scrap.BONDS]
print("-------------------------------------------------")
print("** TOP 5 Облигации в портфеле, отсортированные по стоимости **")
print(df_pcb_bonds[['Наименование','Рыночная стоимость','Сектор','% от полной стоимости портфеля','% от стоимости всех облигаций']].head(5))

# Суммы облигаций, сгруппированные по типу ОФЗ, Субъект или Корпорат
df_tip_grouped_and_aggregated_pcb = df_pcb_bonds.groupby(["Сектор"]).agg({'Рыночная стоимость' : ['sum']})
# Сортируем
# TODO: Попытаться разобраться как работает строчка сортировки ниже (нашёл опытным путём, основа - stack())
df_tip_grouped_and_aggregated_pcb = df_tip_grouped_and_aggregated_pcb.stack().sort_values(by=['Рыночная стоимость'],ascending=False)
# TODO: Убрать sum
# Добавляем столбец - % от стоимости всех облигаций = стомость_типа/стоимость_всех_облигаций
df_tip_grouped_and_aggregated_pcb['% от стоимости всех облигаций'] = df_tip_grouped_and_aggregated_pcb['Рыночная стоимость']*100/dict_portfel[scrap.BONDS]
print("-------------------------------------------------")
print("** Типы в портфеле облигаций, отсортированные по стоимости **")
print(df_tip_grouped_and_aggregated_pcb)

# additional_money = float(input("Введите сумму, которую собираемся доложить на счёт, рублей: "))
additional_money = 0
full_portfel_cost = full_portfel_cost + additional_money
dict_portfel[scrap.CASH] = dict_portfel[scrap.CASH] + additional_money

#print(dict_portfel)

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


# Вывод в консоль
print("-------------------------------------------------")
print("** Параметры портфеля в настоящее время (с учётом докладываемой суммы) **")
print(f"- Стоимость ценных бумаг:    {(full_portfel_cost - dict_portfel[scrap.CASH]):11} рублей")
print(f"- Денежные средства:         {dict_portfel[scrap.CASH]:11} рублей")
print(f"- Полная стоимость портфеля: {full_portfel_cost:11} рублей")
print("-------------------------------------------------")
print("** Доли активов в настоящее время (с учётом докладываемой суммы) **")
print(f"- Облигации, %:          {current_portions[scrap.BONDS]:5}")
print(f"- Акции, %:              {current_portions[scrap.SHARES]:5}")
print(f"- Золото, %:             {current_portions[scrap.GOLD]:5}")
print(f"- Денежные средства, %:  {current_portions[scrap.CASH]:5}")
print("-------------------------------------------------")
print("** Необходимые изменения для достижения идеальных пропорций **")
if diff_portions[scrap.BONDS]>0:
    print(f"- Облигации:    купить на {diff_portions[scrap.BONDS]:11} рублей")
else:
    print(f"- Облигации:    продать на {abs(diff_portions[scrap.BONDS]):11} рублей")
if diff_portions[scrap.SHARES]>0:
    print(f"- Акции:        купить на {diff_portions[scrap.SHARES]:11} рублей")
else:
    print(f"- Акции:        продать на {abs(diff_portions[scrap.SHARES]):11} рублей")
if diff_portions[scrap.GOLD]>0:
    print(f"- Золото:       купить на {diff_portions[scrap.GOLD]:11} рублей")
else:
    print(f"- Золото:       продать на {abs(diff_portions[scrap.GOLD]):11} рублей")


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
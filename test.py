''' Отдельный модуль для "обкатки" функционала '''

from modules import scrap

REPORT_PATH = r"C:\Users\User\Desktop\brokercode_030719_030719_D.html"

temp = scrap.get_info(REPORT_PATH)

print(temp)
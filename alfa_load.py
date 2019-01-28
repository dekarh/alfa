# -*- coding: utf-8 -*-
# Робот, ежечасно переносящий из Сатурна в Tinkoff

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import sys
import datetime
from mysql.connector import MySQLConnection, Error

from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from lib_scan import wj, p, chk
from alfa_env import clicktity, inputtity, inputtity_first, selectity, select_selectity, gluk_w_point

import time

# DRIVER_PATH = 'drivers/chromedriver.exe'
#DRIVER_PATH = 'drivers/chromedriver'


def authorize(driver, login, password, authorize_page=''):
    if authorize_page != '':
        driver.get(authorize_page)
    # Ввод логина
    elem = driver.find_element_by_name("login")
    elem.send_keys(login)

    # Ввод пароля
    elem = driver.find_element_by_name("password")
    elem.send_keys(password)

    # Отправка формы нажатием кнопки
    elem = driver.find_element_by_name('go')
    elem.click()

def my_input2(driver, a, res, inp):
    for pole in a:
        if res[pole] != None:
            if res[pole] != '':
                elem = p(d=driver, f='c', **inp[pole])
                elem.send_keys(' ')
                elem.clear()
                elem.send_keys(' ')
                elem.send_keys(res[pole])
#                for iq in range(1,150):
#                    elem.send_keys(Keys.BACKSPACE)
#                for fucked_char in res[pole]:
#                    elem.send_keys(fucked_char)
                wj(driver)
                elem = p(d=driver, f='p', **inp['ЩелчокДляСброса'])
                wj(driver)
                elem.click()
                wj(driver)

def my_input(driver, a, res, inp):
    for pole in a:
        if res[pole] != None:
            if res[pole] != '':
                elem = p(d=driver, f='c', **inp[pole])
    #            wj(driver)
    #            elem.click()
    #            wj(driver)
    #            elem.clear()
                wj(driver)
                if pole in ['УлицаРАБ', 'УлицаРЕГ', 'УлицаФАКТ']:
                    res[pole] = s_minus(res[pole]).replace('.',' ')
                for fucked_char in s(res[pole]):
                    elem.send_keys(fucked_char)

                wj(driver)
                elem = p(d=driver, f='p', **inp['ЩелчокДляСброса'])
                wj(driver)
                elem.click()
                wj(driver)


# driver = webdriver.Chrome(DRIVER_PATH)  # Инициализация драйвера
#driver = webdriver.Firefox()  # Инициализация драйвера

webconfig = read_config(filename='alfa.ini', section='web')
fillconfig = read_config(filename='alfa.ini', section='fill')
dbconfig = read_config(filename='alfa.ini', section='SaturnFIN')

conn = MySQLConnection(**dbconfig) # Открываем БД из конфиг-файла
cursor = conn.cursor()

## Формируем SQL по которому будем выгружать
sql = 'SELECT '
for i, inp_i in enumerate(clicktity):
    if str(type(clicktity[inp_i]['SQL']))=="<class 'str'>" and clicktity[inp_i]['SQL'] != '':
        sql += clicktity[inp_i]['SQL'] + ','

for i, inp_i in enumerate(inputtity):
    if str(type(inputtity[inp_i]['SQL']))=="<class 'str'>" and inputtity[inp_i]['SQL'] != '':
        sql += inputtity[inp_i]['SQL'] + ','

for i, sel_i in enumerate(selectity):
    if selectity[sel_i]['SQL'] != '':
        sql += selectity[sel_i]['SQL'] + ','

sql = sql[:len(sql) - 1] + " FROM clients AS a INNER JOIN contracts AS b ON a.client_id=b.client_id WHERE b.status_code=0"

#sql = "SELECT banks.bank_id, banks.bank_name, banks.type_rasch, banks.per_day, banks.koef_185_fz, " \
#      "gar_banks.delta, gar_banks.summ, gar_banks.perc_fz_44, gar_banks.min_fz_44 FROM gar_banks,banks" \
#      " WHERE (gar_banks.bank_id = banks.bank_id) AND (banks.per_day = TRUE) AND (gar_banks.delta >= %s)" \
#      " AND (gar_banks.summ >= %s) ORDER BY (gar_banks.delta - %s), (gar_banks.summ - %s)"
#cursor.execute(sql, (delta.days, summ, delta.days, summ))
cursor.execute(sql)
rows = cursor.fetchall()
conn.close()

print('\n'+ datetime.datetime.now().strftime("%H:%M:%S") +' Скрипт выгрузки. Начинаем \n')

if len(rows) == 0:
    print('\n'+ datetime.datetime.now().strftime("%H:%M:%S") + ' Нет новых договоров. Работа скрипта окончена')
    sys.exit()

driver = webdriver.Chrome()  # Инициализация драйвера
driver.implicitly_wait(10)
authorize(driver, **webconfig)  # Авторизация
driver.get(**fillconfig)  # Открытие страницы
time.sleep(1)


for k, row in enumerate(rows):                    # Цикл по строкам таблицы (основной)
    j = 0
    res_cli = {}
    for i, inp_i in enumerate(clicktity):
        if str(type(clicktity[inp_i]['SQL'])) == "<class 'str'>" and clicktity[inp_i]['SQL'] != '':
            if row[j] == None:
                res_cli[inp_i] = 0
            else:
                res_cli[inp_i] = row[j]
            j += 1

    res_inp = {}
    res_sel = {}
    for i, inp_i in enumerate(inputtity):
        if str(type(inputtity[inp_i]['SQL'])) == "<class 'str'>" and inputtity[inp_i]['SQL'] != '':
            if inp_i in ('МестоРождения'):
                res_inp[inp_i] = filter_rus_sp(row[j]).replace('.',' ')
            elif inp_i in ('Фамилия', 'Имя', 'Отчество', 'ИмяДопТелефон'):
                res_inp[inp_i] = filter_rus_minus(row[j])
            elif inp_i in ('СНИЛС'):
                res_inp[inp_i] = '{:011d}'.format(l(row[j]))
            elif inp_i in ('МобТелефон', 'ДопТелефон', 'ТелефонРАБ'):
                res_inp[inp_i] = '{:011d}'.format(l(row[j]))[1:]
            else:
                res_inp[inp_i] = row[j]
            j += 1

    for i, sel_i in enumerate(selectity):
        if selectity[sel_i]['SQL'] != '':
            res_sel[sel_i] = row[j]
            j += 1

    driver.switch_to.frame(driver.find_element_by_tag_name("iframe")) # Переключаемся во фрейм
    elem = p(d = driver, f = 'c', **clicktity['cAddrFACTtoo'])  # Адреса регистрации и проживания всегда отличаются
    wj(driver)
    elem.click()
    wj(driver)
    elem = p(d = driver, f = 'c', **selectity['ТипЗанятости']) # Тип занятости
    wj(driver)
    elem.click()
    elem = p(d = driver, f = 'c', **select_selectity['ТипЗанятости'][int(res_sel['ТипЗанятости'])])
    wj(driver)
    elem.click()
    if int(res_sel['ТипЗанятости']) == 0:                           # Работаю
        my_input(driver, ['НазвДолжности'], res_inp, inputtity)
        elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
        wj(driver)
        elem.click()
        elem = p(d=driver, f='c', **selectity['Должность'])
        wj(driver)
        elem.click()
        elem = p(d=driver, f='c', **select_selectity['Должность'][l(res_sel['Должность'])])
        wj(driver)
        elem.click()
        elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
        wj(driver)
        elem.click()
        elem = p(d=driver, f='c', **selectity['Стаж'])
        wj(driver)
        elem.click()
        elem = p(d=driver, f='c', **select_selectity['Стаж'][l(res_sel['Стаж'])])
        wj(driver)
        elem.click()
        wj(driver)

    elif int(res_sel['ТипЗанятости']) == 1: # Бизнес
        if res_cli['cBisUnOfficial'] == 1:
            elem = p(d=driver, f='c', **clicktity['cBisUnOfficial'])
            wj(driver)
            elem.click()
            wj(driver)
    else:                                   # Не работаю
        elem = p(d=driver, f='c', **select_selectity['ТипНезанятости'][int(res_sel['ТипНезанятости'])])
        wj(driver)
        elem.click()
        if int(res_sel['ТипНезанятости']) == 4:                     #  Заполняем Не работаю-Другое
            my_input(driver, ['НеРаботаю-Другое'], res_inp, inputtity)

    if int(res_sel['ТипЗанятости']) <= 1:                           # Работаю или Бизнес
        my_input(driver, ['НазвФирмы', 'ТелефонРАБ'], res_inp, inputtity)

        probel = ''
        if s(res_inp['РайонРАБ']) != '' and s(res_inp['ГородРАБ']) != '':
            probel = ' '
        res_inp['РайонРАБ'] = s(res_inp['РайонРАБ']) + probel + s(res_inp['ГородРАБ'])
        if s(res_inp['НасПунктРАБ']) == '':
            res_inp['НасПунктРАБ'] = s(res_inp['РайонРАБ'])
        if s(res_inp['УлицаРАБ']) == '':
            res_inp['УлицаРАБ'] = s(res_inp['НасПунктРАБ'])
        if lenl(res_inp['ИндексРАБ']) != 0:
            my_input(driver, ['ИндексРАБ'], res_inp, inputtity)
        if chk(d=driver, f='p', **clicktity['ПроверкаИндекса']):
            elem = p(d=driver, f='p', **inputtity['ИндексРАБ'])
            wj(driver)
            elem.clear()
            wj(driver)
            elem.send_keys(' ')
            wj(driver)
        if chk(d=driver, f='p', **inputtity['РегионРАБ']):
            if p(d=driver, f='p', **inputtity['РегионРАБзнач']) == '':
                my_input(driver, ['РегионРАБ'], res_inp, inputtity)
        if chk(d=driver, f='p', **inputtity['РайонРАБ']):
            if p(d=driver, f='p', **inputtity['РайонРАБзнач']) == '':
                my_input(driver, ['РайонРАБ'], res_inp, inputtity)
        if chk(d=driver, f='p', **inputtity['НасПунктРАБ']):
            if p(d=driver, f='p', **inputtity['НасПунктРАБзнач']) == '':
                my_input(driver, ['НасПунктРАБ'], res_inp, inputtity)
        if chk(d=driver, f='p', **inputtity['УлицаРАБ']):
            if p(d=driver, f='p', **inputtity['УлицаРАБзнач']) != '':
                elem = p(d=driver, f='p', **inputtity['УлицаРАБ'])
                wj(driver)
                elem.clear()
                wj(driver)
                elem.send_keys(Keys.BACKSPACE)
                wj(driver)
                elem.send_keys(' ')
        my_input(driver, ['УлицаРАБ', 'ДомРАБ', 'КорпусРАБ', 'НомОфисаРАБ'], res_inp, inputtity)

    probel = ''
    if s(res_inp['РайонРЕГ']) != '' and s(res_inp['ГородРЕГ']) != '':
        probel = ' '
    res_inp['РайонРЕГ'] = s(res_inp['РайонРЕГ']) + probel + s(res_inp['ГородРЕГ'])
    if s(res_inp['НасПунктРЕГ']) == '':
        res_inp['НасПунктРЕГ'] = s(res_inp['РайонРЕГ'])
    if s(res_inp['УлицаРЕГ']) == '':
        res_inp['УлицаРЕГ'] = s(res_inp['НасПунктРЕГ'])
    if lenl(res_inp['ИндексРЕГ']) != 0:
        my_input(driver, ['ИндексРЕГ'], res_inp, inputtity)
    if chk(d=driver, f='p', **clicktity['ПроверкаИндекса']):
        elem = p(d=driver, f='p', **inputtity['ИндексРЕГ'])
        wj(driver)
        elem.clear()
        wj(driver)
        elem.send_keys(' ')
        wj(driver)
    if chk(d=driver, f='p', **inputtity['РегионРЕГ']):
        if p(d=driver, f='p', **inputtity['РегионРЕГзнач']) == '':
            my_input(driver, ['РегионРЕГ'], res_inp, inputtity)
    if chk(d=driver, f='p', **inputtity['РайонРЕГ']):
        if p(d=driver, f='p', **inputtity['РайонРЕГзнач']) == '':
            my_input(driver, ['РайонРЕГ'], res_inp, inputtity)
    if chk(d=driver, f='p', **inputtity['НасПунктРЕГ']):
        if p(d=driver, f='p', **inputtity['НасПунктРЕГзнач']) == '':
            my_input(driver, ['НасПунктРЕГ'], res_inp, inputtity)
    if chk(d=driver, f='p', **inputtity['УлицаРЕГ']):
        if p(d=driver, f='p', **inputtity['УлицаРЕГзнач']) != '':
            elem = p(d=driver, f='p', **inputtity['УлицаРЕГ'])
            wj(driver)
            elem.clear()
            wj(driver)
            elem.send_keys(Keys.BACKSPACE)
            wj(driver)
            elem.send_keys(' ')
    my_input(driver, ['УлицаРЕГ', 'ДомРЕГ', 'КорпусРЕГ', 'КвартираРЕГ'], res_inp, inputtity)

    probel = ''
    if s(res_inp['РайонФАКТ']) != '' and s(res_inp['ГородФАКТ']) != '':
        probel = ' '
    res_inp['РайонФАКТ'] = s(res_inp['РайонФАКТ']) + probel + s(res_inp['ГородФАКТ'])
    if s(res_inp['НасПунктФАКТ']) == '':
        res_inp['НасПунктФАКТ'] = s(res_inp['РайонФАКТ'])
    if s(res_inp['УлицаФАКТ']) == '':
        res_inp['УлицаФАКТ'] = s(res_inp['НасПунктФАКТ'])
    if lenl(res_inp['ИндексФАКТ']) != 0:
        my_input(driver, ['ИндексФАКТ'], res_inp, inputtity)
    if chk(d=driver, f='p', **clicktity['ПроверкаИндекса']):
        elem = p(d=driver, f='p', **inputtity['ИндексФАКТ'])
        wj(driver)
        elem.clear()
        wj(driver)
        elem.send_keys(' ')
        wj(driver)
    if chk(d=driver, f='p', **inputtity['РегионФАКТ']):
        if p(d=driver, f='p', **inputtity['РегионФАКТзнач']) == '':
            my_input(driver, ['РегионФАКТ'], res_inp, inputtity)
    if chk(d=driver, f='p', **inputtity['РайонФАКТ']):
        if p(d=driver, f='p', **inputtity['РайонФАКТзнач']) == '':
            my_input(driver, ['РайонФАКТ'], res_inp, inputtity)
    if chk(d=driver, f='p', **inputtity['НасПунктФАКТ']):
        if p(d=driver, f='p', **inputtity['НасПунктФАКТзнач']) == '':
            my_input(driver, ['НасПунктФАКТ'], res_inp, inputtity)
    if chk(d=driver, f='p', **inputtity['УлицаФАКТ']):
        if p(d=driver, f='p', **inputtity['УлицаФАКТзнач']) != '':
            elem = p(d=driver, f='p', **inputtity['УлицаФАКТ'])
            wj(driver)
            elem.clear()
            wj(driver)
            elem.send_keys(Keys.BACKSPACE)
            wj(driver)
            elem.send_keys(' ')
    my_input(driver, ['УлицаФАКТ', 'ДомФАКТ', 'КорпусФАКТ', 'КвартираФАКТ'], res_inp, inputtity)
    fio = res_inp['Фамилия'] + ' ' + res_inp['Имя'] + ' ' + res_inp['Отчество']
    my_input(driver, ['Фамилия', 'Имя', 'Отчество', 'МобТелефон', 'КредЛимит', 'Email'], res_inp, inputtity)
    if l(res_inp['СНИЛС']) > 0:
        my_input(driver, ['СНИЛС'], res_inp, inputtity)
    elem = p(d=driver, f='p', **clicktity['ПодтвФамилии'])  # Подверждаем фамилию и телефон
    wj(driver)
    if elem != None:
        elem.click()
    wj(driver)
    elem = p(d=driver, f='c', **clicktity['ПодтвМобТел'])
    wj(driver)
    if elem != None:
        elem.click()
    wj(driver)
    elem = p(d=driver, f='p', **clicktity['ПодтвИмени'])  # Подверждаем фамилию и телефон
    wj(driver)
    if elem != None:
        elem.click()
    wj(driver)
    elem = p(d=driver, f='p', **clicktity['ПодтвОтчества'])  # Подверждаем фамилию и телефон
    wj(driver)
    if elem != None:
        elem.click()
    wj(driver)
#    res_inp['МестоРождения'] = res_inp['МестоРождения'].replace('.',' ').replace('  ',' ').replace('  ',' ')
    my_input(driver, ['ДатаРождения', 'СерияНомер', 'МестоРождения', 'КодПодразд', 'ДатаВыдачи'], res_inp, inputtity)
    res_inp['КемВыдан'] = res_inp['КемВыдан'].replace('.', ' ').replace('  ', ' ').replace('  ', ' ')
    my_input2(driver, ['КемВыдан'], res_inp, inputtity)

    my_input(driver, ['ДопТелефон'], res_inp, inputtity)
    wj(driver)
    elem = p(d = driver, f = 'c', **selectity['ВладелецДопТелефона'])
    wj(driver)
    elem.click()
    elem = p(d = driver, f = 'c', **select_selectity['ВладелецДопТелефона'][l(res_sel['ВладелецДопТелефона'])])
    wj(driver)
    elem.click()
    wj(driver)
    if l(res_sel['ВладелецДопТелефона']) > 0:
        my_input(driver, ['ИмяДопТелефон'], res_inp, inputtity)
    my_input(driver, ['ПерсДоход', 'КвартПлата'], res_inp, inputtity)
    wj(driver)
    elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
    wj(driver)
    elem.click()
    wj(driver)
    if l(res_sel['ПлатежиКредитные']) > 0:
        elem = p(d = driver, f = 'c', **selectity['ПлатежиКредитные'])
        wj(driver)
        elem2 = p(d = driver, f = 'p', **select_selectity['ПлатежиКредитные'][l(res_sel['ПлатежиКредитные'])])
        wj(driver)
        while not elem2.is_displayed():
            elem.click()
        wj(driver)
        elem = p(d = driver, f = 'c', **select_selectity['ПлатежиКредитные'][l(res_sel['ПлатежиКредитные'])])
        wj(driver)
        elem.click()
        wj(driver)
        elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
        wj(driver)
        elem.click()
        wj(driver)
    if l(res_sel['КредитнаяИстория']) > 0:
        elem = p(d = driver, f = 'c', **selectity['КредитнаяИстория'])
        wj(driver)
        elem2 = p(d = driver, f = 'p', **select_selectity['КредитнаяИстория'][l(res_sel['КредитнаяИстория'])])
        wj(driver)
        while not elem2.is_displayed():
            elem.click()
        wj(driver)
        elem = p(d = driver, f = 'c', **select_selectity['КредитнаяИстория'][l(res_sel['КредитнаяИстория'])])
        wj(driver)
        elem.click()
        wj(driver)
        elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
        wj(driver)
        elem.click()
        wj(driver)
    if l(res_sel['Образование']) > 0:
        elem = p(d = driver, f = 'c', **selectity['Образование'])
        wj(driver)
        elem2 = p(d=driver, f='p', **select_selectity['Образование'][l(res_sel['Образование'])])
        wj(driver)
        while not elem2.is_displayed():
            elem.click()
        wj(driver)
        elem = p(d = driver, f = 'c', **select_selectity['Образование'][l(res_sel['Образование'])])
        wj(driver)
        elem.click()
        wj(driver)
        elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
        wj(driver)
        elem.click()
        wj(driver)
    if l(res_sel['СемейноеПоложение']) > 0:
        elem = p(d = driver, f = 'c', **selectity['СемейноеПоложение'])
        wj(driver)
        elem2 = p(d = driver, f = 'p', **select_selectity['СемейноеПоложение'][l(res_sel['СемейноеПоложение'])])
        wj(driver)
        while not elem2.is_displayed():
            elem.click()
        wj(driver)
        elem = p(d = driver, f = 'c', **select_selectity['СемейноеПоложение'][l(res_sel['СемейноеПоложение'])])
        wj(driver)
        elem.click()
        wj(driver)
        elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
        wj(driver)
        elem.click()
        wj(driver)
    elem = p(d = driver, f = 'c', **selectity['Автомобиль'])
    wj(driver)
    elem2 = p(d = driver, f = 'p', **select_selectity['Автомобиль'][int(res_sel['Автомобиль'])])
    wj(driver)
    while not elem2.is_displayed():
        elem.click()
    wj(driver)
    elem = p(d = driver, f = 'c', **select_selectity['Автомобиль'][int(res_sel['Автомобиль'])])
    wj(driver)
    elem.click()
    wj(driver)
    elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
    wj(driver)
    elem.click()
    wj(driver)
    if l(res_sel['Автомобиль']) > 0:
        my_input(driver, ['МаркаАвто', 'МодельАвто', ], res_inp, inputtity)
        elem = p(d=driver, f='c', **clicktity['НетКАСКО'])
        wj(driver)
        if res_cli['НетКАСКО'] == 1:
            elem.click()
            wj(driver)
        else:
            my_input(driver, ['ДатаКАСКОАвто'], res_inp, inputtity)
        if l(res_sel['ГодАвто']) > 1969 and l(res_sel['ГодАвто']) <= datetime.datetime.now().year :
            elem = p(d=driver, f='c', **selectity['ГодАвто']) #.get_attribute('innerHTML')
            wj(driver)
            open_selectity = {'t': 'x', 's': '//SPAN[text()="Год выпуска"]/following-sibling::*',
                              'txt': str(res_sel['ГодАвто'])}
            manual_selectity = {'t': 'x', 's': '//SPAN[text()="' + str(res_sel['ГодАвто']) + '"]',
                                'txt': str(res_sel['ГодАвто'])}
            elem2 = p(d=driver, f='p', **manual_selectity)
            wj(driver)
            m = 0
            while not elem2.is_displayed():
                elem.click()
                m += 1
                if m > 10:
                    break
            wj(driver)
            for i in range(datetime.datetime.now().year,1969,-1):
                elem.send_keys(Keys.ARROW_DOWN)
            elem = p(d=driver, f='c', **manual_selectity)
            wj(driver)
            elem.click()
            elem = p(d=driver, f='p', **inputtity['ЩелчокДляСброса'])
            wj(driver)
            elem.click()
            wj(driver)
    if res_cli['ЕстьЗагранПаспорт'] > 0:
        elem = p(d=driver, f='c', **clicktity['ЕстьЗагранПаспорт'])
        wj(driver)
        elem.click()
        elem = p(d=driver, f='c', **clicktity['ПредоставлюЗагранПаспорт'])
        wj(driver)
        elem.click()
        if l(res_sel['ЧастоЗагран']) > 0:
            elem = p(d=driver, f='c', **selectity['ЧастоЗагран'])
            wj(driver)
            elem2 = p(d=driver, f='p', **select_selectity['ЧастоЗагран'][int(res_sel['ЧастоЗагран'])])
            wj(driver)
            while not elem2.is_displayed():
                elem.click()
            wj(driver)
            elem = p(d=driver, f='c', **select_selectity['ЧастоЗагран'][int(res_sel['ЧастоЗагран'])])
            wj(driver)
            elem.click()
            wj(driver)

    elem = p(d=driver, f='c', **clicktity['Оформить'])  # Нажимаем кнопку Оформить
    wj(driver)
    elem.click()
    wj(driver)

    conn = MySQLConnection(**dbconfig)  # Открываем БД из конфиг-файла
    cursor = conn.cursor()
    if p(d=driver, f='p', **clicktity['Загружено?']) == None:
        aa = p(d=driver, f='p', **clicktity['Ошибки'])
        print('\n При заполнении анкеты', fio, 'допущены ошибки:' )
#        print( '%s.' % ', '.join(aa))
        print(aa)
        sql = 'UPDATE contracts SET status_code=4, transaction_date=NULL, error_message=%s  WHERE client_id=%s AND id>-1'
        cursor.execute(sql,(aa, res_inp['iId']))
        conn.commit()
    else:
        sql = 'UPDATE contracts SET status_code=5, transaction_date=NOW(), error_message=NULL WHERE client_id=%s AND id>-1'
        cursor.execute(sql, (res_inp['iId'],))
        conn.commit()
    conn.close()

    driver.switch_to.default_content()   # Выходим из iframe

    wj(driver)
    elem = p(d=driver, f='c', **clicktity['СледующаяЗаявка'])  # Следующая заявка
    wj(driver)
    elem.click()
    wj(driver)


# Пока выдает пустую страницу после нажатия "Оформить" и никуда не пускает. Приходится заново входить
#    driver.close()
#    driver = webdriver.Chrome()  # Инициализация драйвера
#    authorize(driver, **webconfig)  # Авторизация
#    driver.get(**fillconfig)  # Открытие страницы
#    time.sleep(1)


driver.close()
print('\n'+ datetime.datetime.now().strftime("%H:%M:%S") + ' Работа скрипта окончена')




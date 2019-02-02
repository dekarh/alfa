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
from alfa_env import orderity, clicktity, inputtity, inputtity_first, selectity, select_selectity, gluk_w_point

import pika
import time
import json

# DRIVER_PATH = 'drivers/chromedriver.exe'
DRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'


def authorize(driver, login, password, authorize_page=''):
    if authorize_page != '':
        driver.get(authorize_page)
    # Ввод логина
    elem = p(d=driver, f='p', **clicktity['Вход'])
    elem.click()


    elem = driver.find_element_by_name("login")
    elem.send_keys(login)

    # Ввод пароля
    elem = driver.find_element_by_name("password")
    elem.send_keys(password)

    # Отправка формы нажатием кнопки
    elem = driver.find_element_by_name('go')
    elem.click()

def callback(ch, method, properties, body):
    print(" [x] Received %r" % (body,))
    myjson = json.loads(bytes.decode(body))
    for i, order in enumerate(orderity):
        if order.get('SQL'):
            fromSQL = myjson
            for stepSQL in order['SQL']:
                fromSQL = fromSQL[stepSQL]
            print(order['SQL'], fromSQL)
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

webconfig = read_config(filename='alfa.ini', section='web')
fillconfig = read_config(filename='alfa.ini', section='fill')
dbconfig = read_config(filename='alfa.ini', section='SaturnFIN')
rabbituser = read_config(filename='alfa.ini', section='RabbitUser')
rabbiturl = read_config(filename='alfa.ini', section='RabbitUrl')


credentials = pika.PlainCredentials(**rabbituser)
parameters = pika.ConnectionParameters(credentials=credentials, **rabbiturl)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

channel.queue_declare(queue='messages', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='messages')

channel.start_consuming()


conn = MySQLConnection(**dbconfig) # Открываем БД из конфиг-файла
cursor = conn.cursor()

# Формируем SQL по которому будем выгружать
sql = 'SELECT '
for i, order in enumerate(orderity):
    if order.get('SQL'):
        sql += order['SQL'] + ','

# b.status_code=0 - условие выгрузки
sql = sql[:-1] + " FROM alfabank_products WHERE status_code = 0"

#sql = "SELECT banks.bank_id, banks.bank_name, banks.type_rasch, banks.per_day, banks.koef_185_fz, " \
#      "gar_banks.delta, gar_banks.summ, gar_banks.perc_fz_44, gar_banks.min_fz_44 FROM gar_banks,banks" \
#      " WHERE (gar_banks.bank_id = banks.bank_id) AND (banks.per_day = TRUE) AND (gar_banks.delta >= %s)" \
#      " AND (gar_banks.summ >= %s) ORDER BY (gar_banks.delta - %s), (gar_banks.summ - %s)"
#cursor.execute(sql, (delta.days, summ, delta.days, summ))
cursor.execute(sql)
rows = cursor.fetchall()

print('\n'+ datetime.datetime.now().strftime("%H:%M:%S") +' Скрипт выгрузки. Начинаем \n')

if len(rows) == 0:
    print('\n'+ datetime.datetime.now().strftime("%H:%M:%S") + ' Нет новых договоров. Работа скрипта окончена')
    sys.exit()

#driver = webdriver.Firefox()  # Инициализация драйвера
driver = webdriver.Chrome(DRIVER_PATH)  # Инициализация драйвера
driver.implicitly_wait(10)
# authorize(driver, **webconfig)  # Авторизация

for k, row in enumerate(rows):                    # Цикл по строкам таблицы (основной) check absence
    driver.get(**fillconfig)  # Открытие страницы заполнения
    time.sleep(1)
    for i, order in enumerate(orderity):
        if order.get('check'):
            data4send = {'t': 'x', 's': order['check']}
            elem = p(d=driver, f='p', **data4send)
            wj(driver)
            if not elem:
                continue
            if elem.get_attribute('value'):
                continue
        if order.get('check-with-name'):
            elems = driver.find_elements_by_xpath(order['check-with-name'])
            wj(driver)
            has_name = False
            for elem in elems:
                if elem.text.find(order['alfa']) > -1:
                    has_name = True
            if not has_name:
                continue
        if order.get('check-absence'):
            data4send = {'t': 'x', 's': order['check-absence']}
            elem = p(d=driver, f='p', **data4send)
            wj(driver)
            if elem:
                continue
        if order.get('pre-click'):
            data4send = {'t': 'x', 's': order['pre-click']}
            elem = p(d=driver, f='p', **data4send)
            wj(driver)
            elem.click()
        if order.get('click'):
            data4send = {'t': 'x', 's': order['click']}
            elem = p(d=driver, f='p', **data4send)
            wj(driver)
            elem.click()
        fromSQL = ''
        if order.get('SQL'):
            fromSQL = row[cursor.column_names.index(order['SQL'].strip('"'))]
        if fromSQL and order.get('input'):
            data4send = {'t': 'x', 's': order['input']}
            elem = p(d=driver, f='p', **data4send)
            wj(driver)
            elem.send_keys(' ')
            elem.clear()
            elem.send_keys(' ')
            elem.send_keys(fromSQL)
            wj(driver)
        if fromSQL and order.get('char-input'):
            data4send = {'t': 'x', 's': order['char-input']}
            elem = p(d=driver, f='c', **data4send)
            wj(driver)
            for char in s(fromSQL):
                elem.send_keys(char)
            wj(driver)
        if str(fromSQL) != 'None' and str(order.get('select')) != 'None':
            if len(order['select']) >= int(fromSQL):
                data4send = {'t': 'x', 's': order['select'][int(fromSQL)]}
                elem = p(d=driver, f='p', **data4send)
                wj(driver)
                elem.click()
        if order.get('post-click'):
            data4send = {'t': 'x', 's': order['post-click']}
            elem = p(d=driver, f='p', **data4send)
            wj(driver)
            elem.click()


driver.close()
conn.close()
print('\n'+ datetime.datetime.now().strftime("%H:%M:%S") + ' Работа скрипта окончена')




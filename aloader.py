
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import os, sys

from alfa_env import DRIVER_PATH, LOG_FILE, BAD_TRANSACTION_LOG_FILE, orderity
from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from lib_scan import wj, p, chk

webconfig = read_config(filename='alfa.ini', section='web')
fillconfig = read_config(filename='alfa.ini', section='fill')
pid = os.getpid()

myjson = sys.stdin.readline().rstrip()

driver = webdriver.Chrome(DRIVER_PATH)  # Инициализация драйвера
driver.implicitly_wait(10)

try:
    driver.get(**fillconfig)  # Открытие страницы заполнения
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
        if order.get('SQL'):            # "Разворачиваем" любой уровень вложенности json
            fromSQL = myjson
            for stepSQL in order['SQL']:
                fromSQL = fromSQL[stepSQL]
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
        if fromSQL and order.get('click-text'):
            data4send = {'t': 'x', 's': order['click-text'] + str(fromSQL) + '"]'}
            elem = p(d=driver, f='c', **data4send)
            wj(driver)
            elem.click()
        if fromSQL and order.get('click-text-up'):
            data4send = {'t': 'x', 's': order['click-text-up'] + str(fromSQL) + '"]/..'}
            elem = p(d=driver, f='c', **data4send)
            wj(driver)
            elem.click()
        if order.get('post-click'):
            data4send = {'t': 'x', 's': order['post-click']}
            elem = p(d=driver, f='p', **data4send)
            wj(driver)
            elem.click()
    q=0
    ch.basic_ack(delivery_tag = method.delivery_tag)
except Exception as e:
    bad_transaction_log = open(BAD_TRANSACTION_LOG_FILE, 'a')
    bad_transaction_log.write('(' + str(pid) + ')' + datetime.datetime.now().strftime("%H:%M:%S") + ': ' + str(myjson) + ' * * * ' + str(e.args) + '\n')
    driver.close()
    bad_transaction_log.close()
else:
    log = open(LOG_FILE, 'a')
    log.write('(' + str(pid) + ')' + datetime.datetime.now().strftime("%H:%M:%S") + ': ' + str(myjson) + '\n')
    driver.close()
    log.close()


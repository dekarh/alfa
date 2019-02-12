
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import os, sys
from select import select as check_select
from datetime import datetime, timedelta
import json
import requests
import time

from alfa_env import DRIVER_PATH, LOG_FILE, BAD_TRANSACTION_LOG_FILE, LOG_PATH, orderity, writelog, CYCLES_ORDERITY
from alfa_env import post_status, ALOADER_TIMEOUT, smsity
from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from lib_scan import wj, p, chk

class aloader:
    def __init__(self): # Конструктор класса
        opts = Options()
        #opts.headless=True # Невидимый режим браузера - пока выключим
        self.driver = webdriver.Chrome(DRIVER_PATH, options=opts)
        self.driver.implicitly_wait(10)
        self.driver.stop_client()
        self.bad_log = open(LOG_PATH + BAD_TRANSACTION_LOG_FILE, 'a')
        self.log = open(LOG_PATH + LOG_FILE, 'a')

    def __del__(self):  # Деструктор класса
        self.driver.close()
        self.bad_log.close()
        self.log.close()

    def base(self):
        webconfig = read_config(filename='alfa.ini', section='web')
        fillconfig = read_config(filename='alfa.ini', section='fill')
        pid = os.getpid()
        post_api = read_config(filename='alfa.ini', section='postAPI')
        post_url = post_api['url']

        inp = sys.stdin.readline().rstrip()
        #ajson = json.loads('{"passport_lastname": "Якубович"}')
        ajson = json.loads(inp)
        aid = ajson['click_id']

        loading = ajson['__command']['type'] == 'queue'
        complete_orderity = False
        cycles_orderity = 0
        formatting_error = ''
        tek_order = orderity[0]
        while (not complete_orderity) and cycles_orderity <= CYCLES_ORDERITY and loading:
            try:
                link = ajson['__landing_url'] + '&afclick=' + ajson['click_id']
                # Начинаем заполнять
                writelog(self.log, aid, 'Начинаем заполнять по ссылке' + link + str(ajson), str(pid))
                post_status(post_url, aid, 1, 'Начинаем заполнять', self.log, self.bad_log)
                self.driver.start_client()
                self.driver.get(url=link)
                for i, order in enumerate(orderity):
                    tek_order = order
                    if order.get('check'):
                        data4send = {'t': 'x', 's': order['check']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        if not elem:
                            continue
                        if elem.get_attribute('value'):
                            continue
                    if order.get('check-with-name'):
                        elems = self.driver.find_elements_by_xpath(order['check-with-name'])
                        wj(self.driver)
                        has_name = False
                        for elem in elems:
                            if elem.text.find(order['alfa']) > -1:
                                has_name = True
                        if not has_name:
                            continue
                    if order.get('check-absence'):
                        data4send = {'t': 'x', 's': order['check-absence']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        if elem:
                            continue
                    if order.get('pre-click'):
                        data4send = {'t': 'x', 's': order['pre-click']}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
                    if order.get('pre-wait'):
                        time.sleep(order['pre-wait'])
                    if order.get('click'):
                        data4send = {'t': 'x', 's': order['click']}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
                    fromSQL = ''
                    if order.get('SQL'):            # "Разворачиваем" любой уровень вложенности json
                        fromSQL = ajson
                        for stepSQL in order['SQL']:
                            fromSQL = fromSQL[stepSQL]
                    if fromSQL and order.get('input'):
                        data4send = {'t': 'x', 's': order['input']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
        #                elem.send_keys(' ')
        #                elem.clear()
                        elem.send_keys(fromSQL)
                        wj(self.driver)
                    if fromSQL and order.get('input-tel'):
                        data4send = {'t': 'x', 's': order['input-tel']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        elem.send_keys(' ')
                        elem.clear()
                        elem.send_keys(' ')
                        elem.send_keys(fromSQL[1:])
                        wj(self.driver)
                    if fromSQL and order.get('char-input'):
                        data4send = {'t': 'x', 's': order['char-input']}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        for char in s(fromSQL):
                            elem.send_keys(char)
                        wj(self.driver)
                    if str(fromSQL) != 'None' and str(order.get('select')) != 'None':
                        if len(order['select']) >= int(fromSQL):
                            data4send = {'t': 'x', 's': order['select'][int(fromSQL)]}
                            elem = p(d=self.driver, f='c', **data4send)
                            wj(self.driver)
                            elem.click()
                    if fromSQL and order.get('click-text'):
                        data4send = {'t': 'x', 's': order['click-text'] + str(fromSQL) + '"]'}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
                    if fromSQL and order.get('click-text-up'):
                        data4send = {'t': 'x', 's': order['click-text-up'] + str(fromSQL) + '"]/..'}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
                    if l(fromSQL) == 1 and order.get('checkbox'):
                        data4send = {'t': 'x', 's': order['checkbox']}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
                        stamp = aid + '(' + str(pid) + ')' + datetime.now().strftime("%d-%H:%M:%S")
                        self.driver.save_screenshot(LOG_PATH + stamp + '.png')
                    if fromSQL and order.get('radio-select'):
                        sel = -1
                        for j, select in enumerate(order['radio-select-input']):
                            if fromSQL == select:
                                sel = j
                        if sel > -1:
                            data4send = {'t': 'x', 's': order['radio-select'][sel]}
                            elem = p(d=self.driver, f='c', **data4send)
                            wj(self.driver)
                            elem.click()
                    if order.get('post-wait'):
                        time.sleep(order['post-wait'])
                    if order.get('post-click'):
                        data4send = {'t': 'x', 's': order['post-click']}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
                complete_orderity = True
            except Exception as e:
                cycles_orderity += 1
                data4send = {'t': 'x', 's': '//SPAN[contains(@class,"input_invalid")]//SPAN[@class="input__sub"]'}
                input_errors = p(d=self.driver, f='ps', **data4send)
                input_errors_nulled = []
                formatting_error = ''
                if len(input_errors):
                    for i, input_error in enumerate(input_errors):
                        if input_error.strip(' ').strip('\n').strip(' ').strip('\n').strip(' '):
                            input_errors_nulled.append(input_error)
                    formatting_error = 'Ошибки ввода:'
                    for i, input_error in enumerate(input_errors_nulled):
                        formatting_error += '\n' + str(i) + ') ' + input_error
                    formatting_error += '\n Исправьте ошибки, сохраните и отправьте заявку заново'
                nowtime = datetime.now()
                stamp = aid + '(' + str(pid) + ')' + nowtime.strftime("%d-%H:%M:%S")
                if formatting_error:
                    writelog(self.bad_log, aid, tek_order['alfa'] + formatting_error, str(pid), nowtime)
                    post_status(post_url, aid, 1, formatting_error , self.log, self.bad_log)
                else:
                    writelog(self.bad_log, aid, 'Ошибка транспорта: Отправьте заявку заново через 1 минуту.\nинформация для отдадки:'
                             + tek_order['alfa'] + '\n' + str(ajson) + '\n * * * \n' + str(e), str(pid), nowtime)
                    post_status(post_url, aid, 5, 'Ошибка транспорта: Отправьте заявку заново через 1 минуту', self.log, self.bad_log)
                html_log = open(LOG_PATH + stamp + '.html', 'w')
                html_elem = self.driver.find_element_by_xpath('//HTML')
                html_log.write(html_elem.get_attribute('innerHTML'))
                html_log.close()
                self.driver.save_screenshot(LOG_PATH + stamp + '.png')
                writelog(self.log, aid, 'Ошибка - см. лог ошибок, скриншот, файл html', str(pid), nowtime)
                self.driver.stop_client()

        if complete_orderity:
            sms_start_time = datetime.now()
            server_timeout = False
            uspeh = False
            last_state = 0
            client_timeout = False
            while datetime.now() - sms_start_time < timedelta(minutes=ALOADER_TIMEOUT) and not server_timeout and not uspeh:
                current_stdin = ''
                while datetime.now() - sms_start_time < timedelta(minutes=ALOADER_TIMEOUT) and not current_stdin \
                        and not server_timeout and not uspeh:
                    current_html = self.driver.find_element_by_xpath('//HTML').get_attribute('innerHTML')
                    if current_html.find(' сек<!-- /react-text --></p>') > -1:
                        if last_state != 1:
                            last_state = 1
                            writelog(self.log, aid, 'Ждем СМС', str(pid))
                            post_status(post_url, aid, 2, 'Ждем СМС', self.log, self.bad_log)
                    elif current_html.find('Запросить пароль повторно') > -1:
                        if last_state != 2:
                            last_state = 2
                            writelog(self.log, aid, 'Ждем запроса на СМС', str(pid))
                            post_status(post_url, aid, 3, 'Ждем запроса на СМС', self.log, self.bad_log)
                    elif current_html.find('Ваша заявка на кредитную карту устала ждать :)') > -1:
                        if last_state != 3:
                            last_state = 3
                            server_timeout = True
                    elif current_html.find(', спасибо за оформление заявки на кредитную карту. Ваши дальнейшие шаги:') > -1:
                        if last_state != 4:
                            last_state = 4
                            uspeh = True
                    else:
                        if last_state != 5:
                            last_state = 5
                            writelog(self.log, aid, 'Непонятно чего ждем, похоже aloader сбился', str(pid))
                    time.sleep(1)
                    ready, x, y = check_select([sys.stdin], [], [], 0)
                    if ready:
                        current_stdin = sys.stdin.readline().rstrip()
                if current_stdin:
                    ajson = json.loads(current_stdin)
                    if ajson['__command']['type'] == 'confirm':
                        try:
                            writelog(self.log, aid, 'Получено СМС: ' + str(ajson), str(pid))
                            data4send = {'t': 'x', 's': smsity['Ввести СМС']}
                            elem = p(d=self.driver, f='p', **data4send)
                            wj(self.driver)
                            for k in range(6):
                                elem.send_keys(Keys.BACKSPACE)
                                wj(self.driver)
                            elem.send_keys(ajson['__command']['value'])
                            wj(self.driver)
                        except Exception as e:
                            writelog(self.log, aid, 'Ошибка при отправлении СМС: ' + str(ajson), str(pid))
                            #                    data4send = {'t': 'x', 's': '//DIV[@class="confirmation-modal__body"]'}
                            #                    sms_window = p(d=self.driver, f='p', **data4send)
                            #                    sms_window_htm = '\n-------- окошко запроса пароля --------\n' +\
                            #                                      sms_window.get_attribute('innerHTML')
                            sms_window_htm = ''
                            writelog(self.bad_log, aid, 'Ошибка при отправлении СМС: ' + str(ajson) + sms_window_htm, str(pid))
                            post_status(post_url, aid, 5, 'Ошибка при отправлении СМС, повторите отправку', self.log, self.bad_log)
                    elif ajson['__command']['type'] == 'retry':
                        try:
                            writelog(self.log, aid, 'Получена заявка на запрос СМС: ' + str(ajson), str(pid))
                            data4send = {'t': 'x', 's': smsity['Запросить пароль повторно']}
                            elem = p(d=self.driver, f='c', **data4send)
                            wj(self.driver)
                            elem.click()
                        except Exception as e:
                            writelog(self.log, aid, 'Ошибка при запросе повторной СМС: ' + str(ajson), str(pid))
        #                    data4send = {'t': 'x', 's': '//DIV[@class="confirmation-modal__body"]'}
        #                    sms_window = p(d=self.driver, f='p', **data4send)
        #                    sms_window_htm = '\n-------- окошко запроса пароля --------\n' +\
        #                                      sms_window.get_attribute('innerHTML')
                            sms_window_htm = ''
                            writelog(self.bad_log, aid, 'Ошибка при запросе повторной СМС: ' + str(ajson) + sms_window_htm, str(pid))
                            post_status(post_url, aid, 5, 'Ошибка при запросе повторной СМС, повторите запрос', self.log, self.bad_log)
                if datetime.now() - sms_start_time > timedelta(minutes=ALOADER_TIMEOUT):
                    client_timeout = True
            if server_timeout or client_timeout:
                writelog(self.log, aid, 'Таймаут, нет правильной СМС', str(pid))
                post_status(post_url, aid, 10, 'Таймаут, нет правильной СМС', self.log, self.bad_log)
            elif uspeh:
                writelog(self.log, aid, 'Заявка выгружена', str(pid))
                post_status(post_url, aid, 4, 'Заявка выгружена', self.log, self.bad_log)
        else:
            if loading:
                post_status(post_url, aid, 5, 'Вылетел с ошибкой: ' + str(e), self.log, self.bad_log)
            else:
                post_status(post_url, aid, 5, 'Вылетел с неизвестной ошибкой', self.log, self.bad_log)
                writelog(self.log, aid, 'Вылетел с неизвестной ошибкой', str(pid))

al = aloader()
al.base()
del al

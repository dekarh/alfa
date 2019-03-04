
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
from alfa_env import post_status, ALOADER_TIMEOUT, smsity, DEBUG
from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from lib_scan import wj, p, chk


class KillException(Exception):
    pass


class NoDeliveryException(Exception):
    pass


class RequiredDocumentException(Exception):
    pass


class RequiredPartnerLinkException(Exception):
    pass


class ServerTimeOutException(Exception):
    pass


class UspehException(Exception):
    pass


class TrasferErrorException(Exception):
    pass


class aloader:
    def __init__(self): # Конструктор класса
        opts = Options()
        if not DEBUG:
            opts.headless=True # Невидимый режим браузера
        self.driver = webdriver.Chrome(DRIVER_PATH, options=opts)
        self.driver.implicitly_wait(10)
        self.driver.stop_client()
        self.bad_log = open(LOG_PATH + BAD_TRANSACTION_LOG_FILE, 'a')
        self.log = open(LOG_PATH + LOG_FILE, 'a')
        self.current_stdin = ''

    def __del__(self):  # Деструктор класса
        self.driver.quit()
        self.bad_log.close()
        self.log.close()

    def base(self):
        webconfig = read_config(filename='alfa.ini', section='web')
        fillconfig = read_config(filename='alfa.ini', section='fill')
        self.pid = os.getpid()
        post_api = read_config(filename='alfa.ini', section='postAPI')
        self.post_url = post_api['url']

        inp = sys.stdin.readline().rstrip()
        #ajson = json.loads('{"passport_lastname": "Якубович"}')
        ajson = json.loads(inp)
        self.aid = ajson['click_id']
        if ajson['__landing_url']:
            self.driver.get(url=ajson['__landing_url'] + '&afclick=' + ajson['click_id'])
        else:
            raise RequiredPartnerLinkException
        loading = ajson['__command']['type'] == 'queue'
        complete_orderity = False
        cycles_orderity = 0
        formatting_error = ''
        tek_order = orderity[0]
        while (not complete_orderity) and cycles_orderity <= CYCLES_ORDERITY and loading:
            documents = ''
            try:
                # Начинаем заполнять
                writelog(self.log, self.aid, 'Начинаем заполнять по ссылке' + ajson['__landing_url'] + '&afclick=' +
                         ajson['click_id'] + str(ajson), self.pid)
                post_status(self.post_url, self.aid, 1, 'Начинаем выгрузку на сервер', self.log, self.bad_log)
                for i, order in enumerate(orderity):
                    # Проверяем stdin
                    ready, x, y = check_select([sys.stdin], [], [], 0)
                    if ready:
                        self.current_stdin = sys.stdin.readline().rstrip()
                    if self.current_stdin:
                        bjson = json.loads(self.current_stdin)
                        if bjson['__command']['type'] == 'kill':
                            self.current_stdin = ''
                            raise KillException
                    tek_order = order
                    wj(self.driver)
                    current_html = self.driver.find_element_by_xpath('//HTML').get_attribute('innerHTML')
                    if current_html.find('Ваша заявка на кредитную карту устала ждать :)') > -1:
                        raise ServerTimeOutException
                    if current_html.find('Ваши дальнейшие шаги') > -1:
                        writelog(self.log, self.aid, 'Банк прервал транcфер заявки, чтобы уточнить некоторые данные '
                                 'лично у Вас. Ожидайте звонка из Альфа-Банка', self.pid)
                        post_status(self.post_url, self.aid, 11, 'Банк прервал транcфер заявки, чтобы уточнить '
                                    'некоторые данные лично у Вас. Ожидайте звонка из Альфа-Банка', self.log,
                                    self.bad_log)
                        raise UspehException
                    fromSQL = ''
                    if order.get('SQL'):            # "Разворачиваем" любой уровень вложенности json
                        fromSQL = ajson
                        for stepSQL in order['SQL']:
                            fromSQL = fromSQL[stepSQL]
                    # проверяем на наличие элемента, если нет - пропускаем цикл
                    if order.get('check'):
                        data4send = {'t': 'x', 's': order['check']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        if not elem:
                            continue
                        if elem.get_attribute('value'):
                            continue
                    # проверяем есть ли доставка курьером, если нет - исключение
                    if order.get('check-delivery'):
                        data4send = {'t': 'x', 's': order['check-delivery']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        if not elem:
                            raise NoDeliveryException
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
                    if order.get('check-has-menu'):
                        data4send = {'t': 'x', 's': order['check-has-menu'] + str(fromSQL) + '")]/..'}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        if not elem:
                            raise NoDeliveryException
                    # проверяем на наличие элемента, если нет - ждем пока не появится
                    if order.get('check-until'):
                        data4send = {'t': 'x', 's': order['check-until']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        while not elem:
                            pass
                    # проверяем заполненность поля input, если текст есть - пропускаем цикл
                    if order.get('check-value'):
                        data4send = {'t': 'x', 's': order['check-value']}
                        elem = p(d=self.driver, f='p', **data4send)
                        wj(self.driver)
                        if elem.get_attribute('value'):
                            continue
                    # проверяем на наличие элемента в списке, если ни одного нет - RequiredDocumentException
                    if order.get('check-with-name'):
                        elems = self.driver.find_elements_by_xpath(order['check-with-name'])
                        wj(self.driver)
                        has_name = False
                        documents = ''
                        for elem in elems:
                            if elem.text and elem.text !='Не могу предоставить':
                                documents += ', ' + elem.text
                                if fromSQL:
                                    if elem.text.find(fromSQL) > -1:
                                        has_name = True
                        documents = documents.strip(',').strip()
                        if fromSQL == None and len(elems):
                            raise RequiredDocumentException
                        if len(elems) and not has_name:
                            raise RequiredDocumentException
                    if order.get('pre-wait'):
                        time.sleep(order['pre-wait'])
                    if order.get('click'):
                        data4send = {'t': 'x', 's': order['click']}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
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
                        data4send = {'t': 'x', 's': order['click-text-up'] + str(fromSQL) + '")]/..'}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
                    if l(fromSQL) == 1 and order.get('checkbox'):
                        data4send = {'t': 'x', 's': order['checkbox']}
                        elem = p(d=self.driver, f='c', **data4send)
                        wj(self.driver)
                        elem.click()
#                        stamp = self.aid + '(' + str(self.pid) + ')' + datetime.now().strftime("%d-%H:%M:%S")
#                        self.driver.save_screenshot(LOG_PATH + stamp + '.png')
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
                    if order.get('loaded'):
                        post_status(self.post_url, self.aid, 1, 'передано ' + order['loaded'], self.log, self.bad_log)
                complete_orderity = True
            except ServerTimeOutException:
                raise
            except RequiredPartnerLinkException:
                writelog(self.log, self.aid, 'Необходимо указать партнерскую ссылку - обратитесть к Вашему куратору',
                         self.pid)
                post_status(self.post_url, self.aid, 5,  'Необходимо указать партнерскую ссылку - обратитесть к '
                            'Вашему куратору', self.log, self.bad_log)
                raise
            except NoDeliveryException:
                writelog(self.log, self.aid, 'Для Вашего города доставка курьером невозможна. После '
                            'поступления СМС от банка, пройдите по ссылке, указанной в нем и выберите удобное Вам место'
                            ' получения карты', self.pid)
                post_status(self.post_url, self.aid, 11, 'Этого города нет в списке доставки курьером. Решение - '
                                                         'сказать клиенту: Для Вашего города доставка курьером '
                                'невозможна. Мы для Вас заполнили заявку. В течении часа Вам придет СМС со ссылкой на '
                                             'заполненную заявку. Пройдите по ссылке, выберите удобное Вам место '
                                             'получения карты и отправьте заявку в Альфа-Банк', self.log, self.bad_log)
                raise
            except RequiredDocumentException:
                writelog(self.log, self.aid, 'Для Вашего региона необходимо предоставить один из документов: ' +
                         documents + '.\n Исправьте заявку и отправьте её заново', self.pid)
                post_status(self.post_url, self.aid, 11,  'Для Вашего региона необходимо предоставить один из '
                            'документов: ' + documents + '.\n Исправьте заявку и отправьте её заново',
                            self.log, self.bad_log)
                raise
            except KillException:
                raise
            except UspehException:
                raise
            except Exception as e:
                cycles_orderity += 1
                data4send = {'t': 'x', 's': '//SPAN[contains(@class,"input_invalid")]//SPAN[@class="input__sub"]/..',
                             'a': 'text'}
                input_errors = p(d=self.driver, f='ps', **data4send)
                input_errors_nulled = []
                formatting_error = ''
                if len(input_errors):
                    for i, input_error in enumerate(input_errors):
                        if input_error.strip(' ').strip('\n').strip(' ').strip('\n').strip(' '):
                            input_errors_nulled.append(input_error.replace('\n',': '))
                    formatting_error = 'Ошибки ввода:'
                    for i, input_error in enumerate(input_errors_nulled):
                        formatting_error += '\n' + str(i + 1) + ') ' + input_error
                    formatting_error += '\n. Исправьте ошибки, сохраните и отправьте заявку заново'
                nowtime = datetime.now()
                stamp = self.aid + '(' + str(self.pid) + ')' + nowtime.strftime("%d-%H:%M:%S")
                if formatting_error:
                    writelog(self.bad_log, self.aid, tek_order['alfa'] + formatting_error, self.pid, nowtime)
                    post_status(self.post_url, self.aid, 1, formatting_error , self.log, self.bad_log)
                else:
                    writelog(self.bad_log, self.aid, 'Ошибка транспорта: Отправьте заявку заново.\n'
                            'информация для отладки:' + tek_order['alfa'] + '\n' + str(ajson) + '\n * * * \n' +
                             str(e), self.pid, nowtime)
                    raise TrasferErrorException
                html_log = open(LOG_PATH + stamp + '.html', 'w')
                html_elem = self.driver.find_element_by_xpath('//HTML')
                html_log.write(html_elem.get_attribute('innerHTML'))
                html_log.close()
                self.driver.save_screenshot(LOG_PATH + stamp + '.png')
                writelog(self.log, self.aid, 'Ошибка - см. лог ошибок, скриншот, файл html', self.pid, nowtime)
                self.driver.execute_script('window.open("' + ajson['__landing_url'] + '&afclick=' + ajson['click_id'] +
                                           '","_blank");')
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

        if complete_orderity:
            sms_start_time = datetime.now()
            server_timeout = False
            uspeh = False
            last_state = 0
            client_timeout = False
            while datetime.now() - sms_start_time < timedelta(minutes=ALOADER_TIMEOUT) and not server_timeout and not uspeh:
                while datetime.now() - sms_start_time < timedelta(minutes=ALOADER_TIMEOUT) and not self.current_stdin \
                        and not server_timeout and not uspeh:
                    current_html = self.driver.find_element_by_xpath('//HTML').get_attribute('innerHTML')
                    if current_html.find('Неправильно введен код смс') > -1:
                        if last_state != 1:
                            last_state = 1
                            post_status(self.post_url, self.aid, 5, 'Неправильная СМС, введите заново', self.log,
                                        self.bad_log)
                    elif current_html.find(' сек<!-- /react-text --></p>') > -1:
                        if last_state != 2:
                            last_state = 2
                            writelog(self.log, self.aid, 'Ждем СМС', self.pid)
                            post_status(self.post_url, self.aid, 2, 'Ждем СМС', self.log, self.bad_log)
                    elif current_html.find('Запросить пароль повторно') > -1:
                        if last_state != 3:
                            last_state = 3
                            writelog(self.log, self.aid, 'Ждем запроса на СМС', self.pid)
                            post_status(self.post_url, self.aid, 3, 'Ждем запроса на СМС', self.log, self.bad_log)
                    elif current_html.find('Ваша заявка на кредитную карту устала ждать :)') > -1:
                        raise ServerTimeOutException
                    elif current_html.find('Ваши дальнейшие шаги:') > -1:
                        raise UspehException
                    else:
                        if last_state != 6:
                            last_state = 6
                            writelog(self.log, self.aid, 'Непонятно чего ждем, похоже aloader сбился', self.pid)
                    time.sleep(1)
                    ready, x, y = check_select([sys.stdin], [], [], 0)
                    if ready:
                        self.current_stdin = sys.stdin.readline().rstrip()
                if self.current_stdin:
                    bjson = json.loads(self.current_stdin)
                    if bjson['__command']['type'] == 'confirm':
                        try:
                            self.current_stdin = ''
                            writelog(self.log, self.aid, 'Получено СМС: ' + str(bjson), self.pid)
                            data4send = {'t': 'x', 's': smsity['Ввести СМС']}
                            elem = p(d=self.driver, f='p', **data4send)
                            wj(self.driver)
                            for k in range(6):
                                elem.send_keys(Keys.BACKSPACE)
                                wj(self.driver)
                            elem.send_keys(bjson['__command']['value'])
                            wj(self.driver)
                        except Exception as e:
                            writelog(self.log, self.aid, 'Ошибка при отправлении СМС: ' + str(bjson), self.pid)
                            #                    data4send = {'t': 'x', 's': '//DIV[@class="confirmation-modal__body"]'}
                            #                    sms_window = p(d=self.driver, f='p', **data4send)
                            #                    sms_window_htm = '\n-------- окошко запроса пароля --------\n' +\
                            #                                      sms_window.get_attribute('innerHTML')
                            sms_window_htm = ''
                            writelog(self.bad_log, self.aid, 'Ошибка при отправлении СМС: ' + str(bjson) +
                                     sms_window_htm, self.pid)
                            post_status(self.post_url, self.aid, 5, 'Ошибка при отправлении СМС, повторите отправку',
                                        self.log, self.bad_log)
                    elif bjson['__command']['type'] == 'retry':
                        try:
                            self.current_stdin = ''
                            writelog(self.log, self.aid, 'Получена заявка на запрос СМС: ' + str(bjson), self.pid)
                            data4send = {'t': 'x', 's': smsity['Запросить пароль повторно']}
                            elem = p(d=self.driver, f='c', **data4send)
                            wj(self.driver)
                            elem.click()
                        except Exception as e:
                            writelog(self.log, self.aid, 'Ошибка при запросе повторной СМС: ' + str(bjson), self.pid)
        #                    data4send = {'t': 'x', 's': '//DIV[@class="confirmation-modal__body"]'}
        #                    sms_window = p(d=self.driver, f='p', **data4send)
        #                    sms_window_htm = '\n-------- окошко запроса пароля --------\n' +\
        #                                      sms_window.get_attribute('innerHTML')
                            sms_window_htm = ''
                            writelog(self.bad_log, self.aid, 'Ошибка при запросе повторной СМС: ' + str(bjson)
                                     + sms_window_htm, self.pid)
                            post_status(self.post_url, self.aid, 5, 'Ошибка при запросе повторной СМС, повторите запрос',
                                        self.log, self.bad_log)
                    elif bjson['__command']['type'] == 'kill':
                        self.current_stdin = ''
                        raise KillException

                if datetime.now() - sms_start_time > timedelta(minutes=ALOADER_TIMEOUT):
                    raise ServerTimeOutException
        else:
            if loading:
                raise TrasferErrorException
            else:
                post_status(self.post_url, self.aid, 5, 'Ошибка, повторите отправку', self.log, self.bad_log)
                writelog(self.log, self.aid, 'Вылетел с неизвестной ошибкой', self.pid)


al = aloader()
try:
    al.base()
except KillException:
    post_status(al.post_url, al.aid, 9, 'Aloader удален', al.log, al.bad_log)
except RequiredDocumentException:
    pass
except RequiredPartnerLinkException:
    pass
except NoDeliveryException:
    pass
except ServerTimeOutException:
    writelog(al.log, al.aid, 'Таймаут, нет правильной СМС', al.pid)
    post_status(al.post_url, al.aid, 10, 'Таймаут, нет правильной СМС', al.log, al.bad_log)
except TrasferErrorException:
    post_status(al.post_url, al.aid, 5, 'Ошибка трансфера на сервер, отправьте заявку заново', al.log,
                al.bad_log)
except UspehException as e:
    writelog(al.log, al.aid, 'Заявка выгружена', al.pid)
    post_status(al.post_url, al.aid, 4, 'Заявка выгружена', al.log, al.bad_log)
except Exception as e:
    writelog(al.log, al.aid, 5, 'Вылетел с ошибкой: ' + str(e), al.pid)
    post_status(al.post_url, al.aid, 5, 'Ошибка, повторите последнее действие', al.log, al.bad_log)
finally:
    del al

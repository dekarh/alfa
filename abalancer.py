# -*- coding: utf-8 -*-
# Балансировщик, получающий задания через RabbitMQ, запускающий нужное количество aloader'ов


import sys, os, subprocess
from datetime import datetime
import logging

from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from alfa_env import LOG_FILE, BAD_TRANSACTION_LOG_FILE, LOG_PATH, MAX_PROCESSES, writelog, post_status, DEBUG, VERSION

import pika
import time
import json, requests


def callback(ch, method, properties, body):
    # принимаем json из рэббита
    ajson = json.loads(bytes.decode(body))
    aid = ajson['click_id']

#    ch.basic_ack(delivery_tag=method.delivery_tag)  # !!!!!!!!!!!!!!!!!!!!
#    sys.exit(0)                                     # !!!!!!!!!!!!!!!!!!!!

    if ajson['__command']['type'] == 'kill':
        ch.basic_ack(delivery_tag=method.delivery_tag)
        writelog(log, aid, "Поступил запрос на закрытие aloader'а", 1)
        logging.warning(aid + " Поступил запрос на закрытие aloader'а")
        if aid in procs.keys():
            procs[aid].stdin.write(body + b"\n")
            procs[aid].stdin.flush()
            writelog(log, aid, str(procs[aid].pid) + ' - закрыт', 1)
            logging.warning(aid + ' ' + str(procs[aid].pid) + ' - закрыт')
            post_status(post_url, aid, 9, aid + '(' + str(procs[aid].pid) + ') - закрыт', log, bad_log)
        else:
            logging.warning(aid + " Нет такого aloader'а")

    # удаляем завершенные aloader'ы из procs
    dieds = {}
    for proc in procs:
        if procs[proc].poll() != None:
            dieds[proc] = procs[proc].pid

    for died in dieds:
        procs.pop(died)
        writelog(log, died, str(dieds[died]) + ' - завершился, удаляем', 1)
        logging.warning(aid + ' ' + str(dieds[died]) + ' - завершился, удаляем')

    if ajson['__command']['type'] == 'map':
        ch.basic_ack(delivery_tag=method.delivery_tag)
        writelog(log, aid, "Поступил запрос на обновление списка aloader'ов", 1)
        logging.warning(aid + ' ' + "Поступил запрос на обновление списка aloader'ов. Список действующих:")
        # а мы их уже обновили/удалили в предыдущем цикле, поэтому просто печатаем
        if len(procs):
            for proc in procs:
                logging.warning(proc + ' - ' + str(procs[proc].pid))
        else:
            logging.warning("нет работающих aloader'ов")
            if '.reboot' in os.listdir():
                os.remove('.reboot')
                logging.warning('Найден файл .reboot - выходим')
                sys.exit()
#        if aid in procs.keys():
#            # есть такой aloader - посылаем пустую строку
#            procs[aid].stdin.write(b"\n")
#            procs[aid].stdin.flush()

    # запускаем/удаляем aloader или посылаем запрос СМС или вносим цифры СМС
    if ajson['__command']['type'] == 'queue':
        writelog(log, aid, 'Поступила новая заявка', 1)
        logging.warning(aid + ' Поступила новая заявка')
        if len(procs) > MAX_PROCESSES:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, str(len(procs)) + " aloader'ов - Система перегружена", 1)
            logging.warning(aid + ' ' + str(len(procs)) + " aloader'ов - Система перегружена")
            post_status(post_url, aid, 7, str(len(procs)) + " aloader'ов - Система перегружена", log, bad_log)
            return
        if aid in procs.keys():
            # есть такой aloader - удаляем и создаем новый aloader
            ch.basic_ack(delivery_tag=method.delivery_tag)
            kill_json = {'click_id': aid, '__command': {'type': 'kill', 'value': None}}
            kill_body = bytes(json.dumps(kill_json),encoding='utf-8')
            procs[aid].stdin.write(kill_body + b"\n")
            procs[aid].stdin.flush()
            old = procs[aid].pid
            procs.pop(aid)
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body + b"\n")
            procs[aid].stdin.flush()
            writelog(log, aid, 'Запрос на создание, а такой aloader уже есть - удалили ' + str(old) +
                     ' и создали новый' + str(procs[aid].pid), 1)
            logging.warning(aid + ' Запрос на создание, а такой aloader уже есть - удалили ' + str(old) +
                     ' и создали новый' + str(procs[aid].pid))
        else:
            # создаем новый aloader
            ch.basic_ack(delivery_tag=method.delivery_tag)
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body + b"\n")
            procs[aid].stdin.flush()
            writelog(log, aid, 'Создан новый aloader ' + str(procs[aid].pid), 1)
            logging.warning(aid + ' Создан новый aloader ' + str(procs[aid].pid))
    elif ajson['__command']['type'] == 'retry':
        writelog(log, aid, 'Поступил запрос на СМС от банка', 1)
        logging.warning(aid + ' Поступил запрос на СМС от банка')
        if aid in procs.keys():
            # есть такой aloader - посылаем запрос СМС
            ch.basic_ack(delivery_tag=method.delivery_tag)
            procs[aid].stdin.write(body + b"\n")
            procs[aid].stdin.flush()
            writelog(log, aid, 'Послали запрос на новую СМС (aloader есть)', 1)
            logging.warning(aid + ' Послали запрос на новую СМС (aloader есть)')
        else:
            # Невозможно ввести SMS, нет такого aloader'а
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, "Невозможно запросить SMS, нет такого aloader'а", 1)
            writelog(bad_log, aid, "Невозможно запросить SMS, нет такого aloader'а", 1)
            logging.warning(aid + " Невозможно запросить SMS, нет такого aloader'а")
            post_status(post_url, aid, 8, "Невозможно запросить SMS, нет такого aloader'а", log, bad_log)
    elif ajson['__command']['type'] == 'confirm':
        writelog(log, aid, 'Поступило СМС от банка', 1)
        logging.warning(aid + ' Поступило СМС от банка')
        if aid in procs.keys():
            ch.basic_ack(delivery_tag=method.delivery_tag)
            procs[aid].stdin.write(body + b"\n")
            procs[aid].stdin.flush()
            writelog(log, aid, 'Посылаем цифры из СМС (есть такой aloader)', 1)
            logging.warning(aid + ' Посылаем цифры из СМС (есть такой aloader)')
        else:
            # нет такого aloader'а - ошибка - нужен новый aloader
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, "Невозможно ввести SMS, нет такого aloader'а", 1)
            writelog(bad_log, aid, "Невозможно ввести SMS, нет такого aloader'а", 1)
            logging.warning(aid + " Невозможно ввести SMS, нет такого aloader'а")
            post_status(post_url, aid, 8, "Невозможно ввести SMS, отправьте заявку в очередь заново", log, bad_log)

if DEBUG:
    logging.basicConfig(level=logging.WARNING,format="%(asctime)s:%(levelname)s:%(message)s")
else:
    logging.basicConfig(level=logging.WARNING, filename='warnings.log',format="%(asctime)s:%(levelname)s:%(message)s")

logging.warning('Загружен abalancer ' + VERSION)
aloader = os.path.join(os.path.dirname(__file__), "aloader.py")
log = open(LOG_PATH + LOG_FILE,'a')
bad_log = open(LOG_PATH + BAD_TRANSACTION_LOG_FILE,'a')
post_api = read_config(filename='alfa.ini', section='postAPI')
post_url = post_api['url']

procs = {}

rabbituser = read_config(filename='alfa.ini', section='RabbitUser')
rabbiturl = read_config(filename='alfa.ini', section='RabbitUrl')

credentials = pika.PlainCredentials(**rabbituser)
parameters = pika.ConnectionParameters(credentials=credentials, **rabbiturl)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

#channel.queue_declare(queue='alfabank_100', durable=True)
logging.warning(' [*] Waiting for messages. To exit press CTRL+C')

channel.basic_qos(prefetch_count=1)
channel.basic_consume('alfabank_100',callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    pass
except Exception as e:
    logging.warning('Ошибка: ' + str(e))
    time.sleep(10)
finally:
    bad_log.close()
    log.close()

q="""
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
"""



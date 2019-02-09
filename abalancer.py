# -*- coding: utf-8 -*-
# Балансировщик, получающий задания через RabbitMQ, запускающий нужное количество aloader'ов


import sys, os, subprocess
from datetime import datetime

from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from alfa_env import LOG_FILE, BAD_TRANSACTION_LOG_FILE, LOG_PATH, MAX_PROCESSES, writelog, post_status

import pika
import time
import json, requests

def callback(ch, method, properties, body):
    # принимаем json из рэббита
    ajson = json.loads(bytes.decode(body))
    print(body)
    print(str(ajson))
    aid = ajson['click_id']

#    ch.basic_ack(delivery_tag=method.delivery_tag)  # !!!!!!!!!!!!!!!!!!!!
#    sys.exit(0)                                     # !!!!!!!!!!!!!!!!!!!!

    if ajson['__command']['type'] == 'kill':
        writelog(log, aid, "Поступил запрос на закрытие aloader'а", 1)
        if aid in procs.values():
            old = procs[aid].pid
            procs[aid].kill()
            procs.pop(aid)
            outs.pop(aid)
            errs.pop(aid)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, str(old) + ' - убит', 1)
            post_status(post_url, aid, 9, aid + '(' + str(old) + ') - убит', log, bad_log)

    # удаляем завершенные aloader'ы из procs
    for proc in procs:
        if procs[proc].returncode != None:
            old = procs[aid].pid
            procs.pop(proc)
            outs.pop(proc)
            errs.pop(proc)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, str(old) + ' - завершился, удаляем', 1)

    if ajson['__command']['type'] == 'map':
        writelog(log, aid, "Поступил запрос на обновление списка aloader'ов", 1)
        if procs[proc].returncode != None:
            old = procs[aid].pid
            procs.pop(proc)
            outs.pop(proc)
            errs.pop(proc)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(proc, ' - ', procs[proc].pid, ' - завершился, удаляем')
            writelog(log, aid, str(old) + ' - завершился, удаляем', 1)
        for proc in procs:
            print(proc, ' - ', procs[proc].pid)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # запускаем/удаляем aloader или посылаем запрос СМС или вносим цифры СМС
    if ajson['__command']['type'] == 'queue':
        writelog(log, aid, 'Поступила новая заявка', 1)
        if len(procs) > MAX_PROCESSES:
            writelog(log, aid, str(len(procs)) + " aloader'ов - Система перегружена", 1)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            post_status(post_url, aid, 7, str(len(procs)) + " aloader'ов - Система перегружена", log, bad_log)
            return
        if aid in procs.values():
            # есть такой aloader - удаляем и создаем новый aloader
            old = procs[aid].pid
            procs[aid].kill()
            procs.pop(aid)
            outs.pop(aid)
            errs.pop(aid)
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body + b"\n")
            #out, err = procs[aid].communicate()
            #outs[aid] = out
            #errs[aid] = err
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, 'Запрос на создание, а такой aloader уже есть - удалили ' + str(old) +
                     ' и создали новый' + str(procs[aid].pid), 1)
        else:
            # создаем новый aloader
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body + b"\n")
            #out, err = procs[aid].communicate()
            #outs[aid] = out
            #errs[aid] = err
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, 'Создан новый aloader ' + str(procs[aid].pid), 1)
    elif ajson['__command']['type'] == 'retry':
        writelog(log, aid, 'Поступил запрос на СМС от банка', 1)
        if aid in procs.values():
            # есть такой aloader - посылаем запрос СМС
            procs[aid].stdin.write(body + b"\n")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, 'Послали запрос на новую СМС (aloader есть)', 1)
        else:
            # Невозможно ввести SMS, нет такого aloader'а
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, "Невозможно запросить SMS, нет такого aloader'а", 1)
            writelog(bad_log, aid, "Невозможно запросить SMS, нет такого aloader'а", 1)
            post_status(post_url, aid, 8, "Невозможно запросить SMS, нет такого aloader'а", log, bad_log)
    elif ajson['__command']['type'] == 'confirm':
        writelog(log, aid, 'Поступило СМС от банка', 1)
        if aid in procs.values():
            ch.basic_ack(delivery_tag=method.delivery_tag)
            procs[aid].stdin.write(body + b"\n")
            writelog(log, aid, 'Посылаем цифры из СМС (есть такой aloader)', 1)
        else:
            # нет такого aloader'а - ошибка - нужен новый aloader
            ch.basic_ack(delivery_tag=method.delivery_tag)
            writelog(log, aid, "Невозможно ввести SMS, нет такого aloader'а", 1)
            writelog(bad_log, aid, "Невозможно ввести SMS, нет такого aloader'а", 1)
            post_status(post_url, aid, 8, "Невозможно ввести SMS, нет такого aloader'а", log, bad_log)

aloader = os.path.join(os.path.dirname(__file__), "./aloader.py")
log = open(LOG_PATH + LOG_FILE,'a')
bad_log = open(LOG_PATH + BAD_TRANSACTION_LOG_FILE,'a')
post_api = read_config(filename='alfa.ini', section='postAPI')
post_url = post_api['url']

outs = {}
errs = {}
procs = {}

rabbituser = read_config(filename='alfa.ini', section='RabbitUser')
rabbiturl = read_config(filename='alfa.ini', section='RabbitUrl')

credentials = pika.PlainCredentials(**rabbituser)
parameters = pika.ConnectionParameters(credentials=credentials, **rabbiturl)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

channel.queue_declare(queue='alfabank_100', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='alfabank_100')

try:
    channel.start_consuming()
except BaseException:
    pass
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



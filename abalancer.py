# -*- coding: utf-8 -*-
# Балансировщик, получающий задания через RabbitMQ, запускающий нужное количество aloader'ов


import sys, os, subprocess
from datetime import datetime

from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from alfa_env import LOG_FILE, BAD_TRANSACTION_LOG_FILE, LOG_PATH, MAX_PROCESSES

import pika
import time
import json

def writelog(file, click_id, message, pid=0, date_time=datetime.now()):
    if not pid:
        pid_str = ' NONE '
    elif pid == 1:
        pid_str = ' MAIN '
    else:
        pid_str = str(pid)
    file.write(click_id + '(' + pid_str + ') ' + date_time.strftime("%d-%H:%M:%S") + ' :' + message + '\n')

def callback(ch, method, properties, body):
    # принимаем json из рэббита
    ajson = json.loads(bytes.decode(body))
    print(str(ajson))
    aid = ajson['click_id']
    ajson['type'] = 'NEW'       # !!!!!!!!!!!!!!!!!!!!
    if ajson['type'] == 'NEW':  # !!!!!!!!!!!!!!!!!!!!
        writelog(log, aid, 'Поступила новая заявка', 1)
    elif ajson['type'][:3] == 'SMS':  # !!!!!!!!!!!!!!!!!!!!
        writelog(log, aid, 'Поступило СМС от банка', 1)
    elif ajson['type'] == 'ORDER':  # !!!!!!!!!!!!!!!!!!!!
        writelog(log, aid, 'Поступил запрос на СМС от банка', 1)
    elif ajson['type'] == 'REFRESH':  # !!!!!!!!!!!!!!!!!!!!
        writelog(log, aid, "Поступил запрос на обновление списка aloader'ов", 1)
    elif ajson['type'] == 'KILL':  # !!!!!!!!!!!!!!!!!!!!
        writelog(log, aid, "Поступил запрос на закрытие aloader'а", 1)

    if ajson['type'] == 'KILL':  # !!!!!!!!!!!!!!!!!!!!
        if aid in procs.values():
            old = procs[aid].pid
            procs[aid].kill()
            procs.pop(aid)
            outs.pop(aid)
            errs.pop(aid)
            chs.pop(aid)
            writelog(log, aid, str(old) + ' - убит', 1)

    # удаляем завершенные aloader'ы из procs
    for proc in procs:
        if procs[proc].returncode != None:
            old = procs[aid].pid
            procs.pop(proc)
            outs.pop(proc)
            errs.pop(proc)
            chs[proc].basic_ack(delivery_tag=method.delivery_tag)
            chs.pop(proc)
            writelog(log, aid, str(old) + 'Завершен - удаляем', 1)

    # запускаем/удаляем aloader или посылаем запрос СМС или вносим цифры СМС
    if ajson['type'] == 'NEW':  # !!!!!!!!!!!!!!!!!!!!
        if len(procs) > MAX_PROCESSES:
            log.write(aid + '( MAIN )' + datetime.now().strftime("%d-%H:%M:%S") + ': Система перегружена' + '\n')
            return
        if aid in procs.values():
            # есть такой aloader - удаляем и создаем новый aloader
            old = procs[aid].pid
            procs[aid].kill()
            procs.pop(aid)
            outs.pop(aid)
            errs.pop(aid)
            chs.pop(aid)
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(bytes.decode(body) + b"\n")
            log.write(aid + '( MAIN )' + datetime.now().strftime("%d-%H:%M:%S") +
                      ': Запрос на создание, а такой aloader уже есть - удаляем ' + str(old) + ' и создаем новый' +
                      str(procs[aid].pid) + '\n')
            out, err = procs[aid].communicate()
            outs[aid] = out
            errs[aid] = err
            chs[aid] = ch
        else:
            # создаем новый aloader
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body + b"\n")
            log.write(aid + '( MAIN )' + datetime.now().strftime("%d-%H:%M:%S") + ': Создаем новый aloader' +
                      str(procs[aid].pid) + '\n')
            out, err = procs[aid].communicate()
            outs[aid] = out
            errs[aid] = err
            chs[aid] = ch
    elif ajson['type'] == 'ORDER': # !!!!!!!!!!!!!!!!!!!!
        if aid in procs.values():
            # есть такой aloader - посылаем запрос СМС
            log.write(aid + '( MAIN )' + datetime.now().strftime("%d-%H:%M:%S") +
                      ': Есть такой aloader - посылаем запрос СМС' + '\n')
            procs[aid].stdin.write('ORDER'.encode("utf8") + b"\n")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # Невозможно ввести SMS, нет такого aloader'а
            log.write(aid + '( MAIN )' + datetime.now().strftime("%d-%H:%M:%S") +
                      ": Невозможно ввести SMS, нет такого aloader'а" + '\n')
    elif ajson['type'][:3] == 'SMS': # !!!!!!!!!!!!!!!!!!!!
        if aid in procs.values():
            # есть такой aloader - посылаем результат из СМС
            # !!!!!!!!!!!!! ИСПРАВИТЬ ajson['SMS'].strip()[:4]
            procs[aid].stdin.write(('SMS  ' + ajson['SMS'].strip()[:4]).encode("utf8") + b"\n")
            log.write(aid + '( MAIN )' + datetime.now().strftime("%d-%H:%M:%S") +
                      ': Есть такой aloader - посылаем цифры из СМС' + '\n')
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # нет такого aloader'а - ошибка - нужен новый aloader
            log.write(aid + '( MAIN )' + datetime.now().strftime("%d-%H:%M:%S") +
                      ": нет такого aloader'а - ошибка - нужен новый aloader" + '\n')

            q=0 # !!!!!!!!!!!!!!!!!!!!

aloader = os.path.join(os.path.dirname(__file__), "./aloader.py")
log = open(LOG_PATH + LOG_FILE,'a')
bad_log = open(LOG_PATH + BAD_TRANSACTION_LOG_FILE,'a')

outs = {}
errs = {}
procs = {}
chs = {}


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



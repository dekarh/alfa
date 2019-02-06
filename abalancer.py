# -*- coding: utf-8 -*-
# Балансировщик, получающий задания через RabbitMQ, запускающий нужное количество aloader'ов


import sys, os, subprocess
import datetime
from mysql.connector import MySQLConnection, Error

from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus
from alfa_env import orderity, clicktity, inputtity, inputtity_first, selectity, select_selectity, gluk_w_point

import pika
import time
import json

def callback(ch, method, properties, body):
    # принимаем json из рэббита
    print(" [x] Received %r" % (body,))
    ajson = json.loads(bytes.decode(body))
    # удаляем завершенные aloader'ы из procs
    for proc in procs:
        if procs[proc].returncode == 0:
            procs.pop(proc)
            outs.pop(proc)
            errs.pop(proc)

    aid = ajson['aid']
    # запускаем/удаляем aloader или посылаем запрос СМС или вносим цифры СМС
    if ajson['type'] == 'new': # !!!!!!!!!!!!!!!!!!!!
        if aid in procs.values():
            # есть такой aloader - удаляем и создаем новый aloader
            procs[aid].stdin.write('DIE'.encode("utf8") + b"\n")
            time.sleep(1)
            for proc in procs:
                if procs[proc].returncode == 0:
                    procs.pop(proc)
                    outs.pop(proc)
                    errs.pop(proc)
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body.encode("utf8") + b"\n")
            out, err = procs[aid].communicate()
            outs[aid] = out
            errs[aid] = err
        else:
            # создаем новый aloader
            procs[aid] = subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body.encode("utf8") + b"\n")
            out, err = procs[aid].communicate()
            outs[aid] = out
            errs[aid] = err
    elif ajson['type'] == 'order SMS': # !!!!!!!!!!!!!!!!!!!!
        if aid in procs.values():
            # есть такой aloader - посылаем запрос СМС
            procs[aid].stdin.write('ORDER'.encode("utf8") + b"\n")
        else:
            # нет такого aloader'а - создаем новый aloader
            procs[aid] =  subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body.encode("utf8") + b"\n")
            out, err = procs[aid].communicate()
            outs[aid] = out
            errs[aid] = err
    elif ajson['type'] == 'SMS': # !!!!!!!!!!!!!!!!!!!!
        if aid in procs.values():
            # есть такой aloader - посылаем результат из СМС !!!!!!!!!!!!! ИСПРАВИТЬ ajson['SMS'].strip()[:4]
            procs[aid].stdin.write(('SMS  ' + ajson['SMS'].strip()[:4]).encode("utf8") + b"\n")
        else:
            # нет такого aloader'а - создаем новый aloader
            procs[aid] =  subprocess.Popen([sys.executable, aloader], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            procs[aid].stdin.write(body.encode("utf8") + b"\n")
            out, err = procs[aid].communicate()
            outs[aid] = out
            errs[aid] = err


aloader = os.path.join(os.path.dirname(__file__), "./aloader.py")

outs = {}
errs = {}
procs = {}


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



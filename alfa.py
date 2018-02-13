# -*- coding: utf-8 -*-
# Робот, отмечающий загруженные


import sys
from _datetime import datetime
import time
import os
import csv
from mysql.connector import MySQLConnection, Error
import openpyxl
from openpyxl import Workbook

from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus

# Партнеры, по которым не надо обрезать !!! MIN - 1 шт !!!
OUR_PARTNERS = [45,191,234]
# Коэффициент обрезки
K_HIDDEN = 0.2
# Дата начала обрезки
DATE_HIDE = '2018-02-01'
# До какой даты ставить статус "Отрицательный результат"
DATE_END_OTKAZ = '2017-12-31'


dbconfig = read_config(filename='alfa.ini', section='SaturnFIN')

has_files = False
all_files = os.listdir(path=".")
for all_file in all_files:
    if all_file.endswith(".xlsx"):
        has_files = True
if not has_files:
    sys.exit()

# обнуление скрытых отказов банка (которые раньше были предварительно одобрены)
dbconn = MySQLConnection(**dbconfig)
cursor = dbconn.cursor()
cursor.execute('UPDATE saturn_fin.alfabank_products SET status_hidden = 0 '
               'WHERE status_hidden = 1 AND (status_code = 3 OR status_code = 5)')
dbconn.commit()


# агенты, которые не участвут в срезе
sql = 'SELECT code from saturn_fin.offices_staff WHERE partner_code = %s'
partners = (OUR_PARTNERS[0],)
our_agents = []
for i, partner in enumerate(OUR_PARTNERS):
    if i == 0:
        continue
    sql += ' OR partner_code = %s'
    partners += (OUR_PARTNERS[i],)
cursor = dbconn.cursor()
cursor.execute(sql, partners)
rows = cursor.fetchall()
for row in rows:
    our_agents.append(row[0])

all_files = os.listdir(path=".")
all_files.sort()
for i, all_file in enumerate(all_files):
    bids_in_xls = {}
#    odobr_in_xls = 0
    if all_file.endswith(".xlsx"):

        dbconn = MySQLConnection(**dbconfig)
        # считаем количество одобреных заявок в базе, кроме договоров агентов, которые не участвут в срезе
        sql = 'SELECT count(*) FROM saturn_fin.alfabank_products WHERE inserted_date > %s AND status_code = 2' \
              ' AND (inserted_code NOT IN (SELECT code from saturn_fin.offices_staff WHERE partner_code = %s'
        partners = (DATE_HIDE, OUR_PARTNERS[0])
        for j, partner in enumerate(OUR_PARTNERS):
            if j == 0:
                continue
            sql += ' OR partner_code = %s '
            partners += (OUR_PARTNERS[j],)
        sql += '))'
        cursor = dbconn.cursor()
        cursor.execute(sql, partners)
        rows = cursor.fetchall()
        odobr_in_db = rows[0][0]

        # считаем количество скрытых заявок в базе
        cursor = dbconn.cursor()
        cursor.execute('SELECT count(*) FROM saturn_fin.alfabank_products WHERE status_hidden = 1')
        rows = cursor.fetchall()
        hidden_in_db = rows[0][0]

        # заявки, без статусов: получил карту, отказ, отрицательный результат
        cursor = dbconn.cursor()
        cursor.execute('SELECT t.returned_id, p.inserted_code FROM saturn_fin.alfabank_products AS p '
                       'LEFT JOIN saturn_fin.alfabank_transactions AS t ON p.id = t.product_id '
                       'WHERE status_code != 3 AND status_code != 5 AND status_code != 6')
        bids_in_db = cursor.fetchall()
        dbconn.close()

        print(datetime.now().strftime("%H:%M:%S"),'загружаем', all_file)
        updates = []
        statuses = []
        wb = openpyxl.load_workbook(filename=all_file, read_only=True)
        sheet = wb[wb.sheetnames[0]]
        head = {}
        for j, row in enumerate(sheet.rows):
            if j == 0:
                for k,cell in enumerate(row):
                    head[cell.value] = k
                break
        for j, row in enumerate(sheet.rows):
            if j == 0:
                continue
            remote_id = str(row[head['app_id']].value).strip()
            status = 1
            if row[head['Заполнил30']].value != None:
                if int(str(row[head['Заполнил30']].value).strip()) > 0:
                    status = 7
            if row[head['ПредОдобрение']].value != None:
                if int(str(row[head['ПредОдобрение']].value).strip()) > 0:
                    status = 2
                    if row[head['Дата договора(выдачи)']].value != None:
                        status = 6
                else:
                    status = 3
            bids_in_xls[remote_id] = {'remote_id': remote_id, 'status': status}

#        has_doubles = []
#        for i, up_i in enumerate(updates):                # проверка на дубли - тут не работает
#            for j, up_j in enumerate(updates):
#                if i == j:
#                    continue
#                if updates[i] == updates[j]:
#                    has_doubles.append(updates[i])
#        if len(has_doubles) > 0:                                 # если были дубли - загрузка невозможна
#            print(len(has_doubles), 'дублей в файле', all_file, '- загрузка невозможна' )
#            continue

        bid_in_xls = {}                                  # Считаем сколько есть БД из одобренных
        bids_in_xls_db = []
        bids_in_db_agents = []
        odobr_in_xls = 0
        for bid_in_db in bids_in_db:
            try:
                bid_in_xls = bids_in_xls[bid_in_db[0]]
                bids_in_xls_db.append(bid_in_xls)
                bids_in_db_agents.append(bid_in_db[1])
            except KeyError:
                continue
            if bid_in_db[1] in our_agents:
                q = 0
            else:
                if bid_in_xls['status'] == 6 or bid_in_xls['status'] == 2:
                    odobr_in_xls += 1

        hidden_in_xls = round((odobr_in_db + odobr_in_xls) * K_HIDDEN - hidden_in_db)
        if hidden_in_xls < 0:
            hidden_in_xls = 0
        print('В файле', all_file, 'из', odobr_in_db + odobr_in_xls, 'одобренных будет скрыто', hidden_in_xls)

        statuses = []
        for j, bid_in_xls in enumerate(bids_in_xls_db):
            if bids_in_db_agents[j] in our_agents:
                statuses.append((bid_in_xls['status'], 0, bid_in_xls['remote_id']))
            else:
                if (bid_in_xls['status'] == 2 or bid_in_xls['status'] == 6) and hidden_in_xls > 0:
                    hidden_in_xls -= 1
                    statuses.append((bid_in_xls['status'], 1, bid_in_xls['remote_id']))
                else:
                    statuses.append((bid_in_xls['status'], 0, bid_in_xls['remote_id']))

        gs =  0
        h_i = []
        for j, st in enumerate(statuses):
            if st[1] == 1:
                gs +=1
                h_i.append(st[2])

        try:
            if all_file[:4] == '201':
                os.rename(all_file, 'loaded/' + all_file)
            else:
                os.rename(all_file, 'loaded/' + datetime.now().strftime("%Y-%m-%d_%H_%M") + '_' + all_file)
        except OSError as e:          # errno.ENOENT = no such file or directory
            if e.errno != OSError.errno.ENOENT:
                print('Ошибка при переносе файла в ./loaded/', e)

        dbconn = MySQLConnection(**dbconfig)
        cursor = dbconn.cursor()
        sql = 'UPDATE saturn_fin.alfabank_products AS p LEFT JOIN saturn_fin.alfabank_transactions AS t ' \
              'ON p.id = t.product_id SET p.status_code = %s, p.status_hidden = %s WHERE t.returned_id = %s'
        cursor.executemany(sql, statuses)
        dbconn.commit()

cursor = dbconn.cursor()
cursor.execute('UPDATE saturn_fin.alfabank_products SET status_code = 5 WHERE status_code != 2 AND status_code != 3 '
               'AND status_code != 101 AND status_code != 100 AND status_code != 5 AND status_code != 6 '
               'AND inserted_date < %s', (DATE_END_OTKAZ,))
dbconn.commit()

dbconn.close()




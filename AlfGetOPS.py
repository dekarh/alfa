# -*- coding: utf-8 -*-
# Робот выгружающий из СатурнОПС

import sys
import datetime
import time
import csv
from mysql.connector import MySQLConnection, Error

from lib import read_config, lenl, s_minus, s, l, filter_rus_sp, filter_rus_minus

ALFA_REGIONS = {
    "Адыгея республика" : 1,"Башкортостан республика" : 2,"Бурятия республика" : 3,"Алтай республика" : 4,
    "Дагестан республика" : 5,"Ингушетия республика" : 6,"Кабардино-Балкарская республика" : 7,
    "Калмыкия республика" : 8,"Карачаево-Черкесская республика" : 9,"Карелия республика" : 10,
    "Коми республика" : 11,"Марий Эл республика" : 12,"Мордовия республика" : 13,"Саха /Якутия/ республика" : 14,
    "Северная Осетия - Алания республика" : 15,"Татарстан республика" : 16,"Тыва республика" : 17,
    "Удмуртская республика" : 18,"Хакасия республика" : 19,"Чеченская республика" : 20,
    "Чувашская Республика - Чувашия" : 21,"Алтайский край" : 22,"Краснодарский край" : 23,"Красноярский край" : 24,
    "Приморский край" : 25,"Ставропольский край" : 26,"Хабаровский край" : 27,"Амурская область" : 28,
    "Архангельская область" : 29,"Астраханская область" : 30,"Белгородская область" : 31,"Брянская область" : 32,
    "Владимирская область" : 33,"Волгоградская область" : 34,"Вологодская область" : 35,"Воронежская область" : 36,
    "Ивановская область" : 37,"Иркутская область" : 38,"Калининградская область" : 39,"Калужская область" : 40,
    "Камчатский край" : 41,"Кемеровская область" : 42,"Кировская область" : 43,"Костромская область" : 44,
    "Курганская область" : 45,"Курская область" : 46,"Ленинградская область" : 47,"Липецкая область" : 48,
    "Магаданская область" : 49,"Московская область" : 50,"Мурманская область" : 51,"Нижегородская область" : 52,
    "Новгородская область" : 53,"Новосибирская область" : 54,"Омская область" : 55,"Оренбургская область" : 56,
    "Орловская область" : 57,"Пензенская область" : 58,"Пермский край" : 59,"Псковская область" : 60,
    "Ростовская область" : 61,"Рязанская область" : 62,"Самарская область" : 63,"Саратовская область" : 64,
    "Сахалинская область" : 65,"Свердловская область" : 66,"Смоленская область" : 67,"Тамбовская область" : 68,
    "Тверская область" : 69,"Томская область" : 70,"Тульская область" : 71,"Тюменская область" : 72,
    "Ульяновская область" : 73,"Челябинская область" : 74,"Забайкальский край" : 75,"Ярославская область" : 76,
    "Москва город" : 77,"Санкт-Петербург город" : 78,"Еврейская автономная область" : 79,
    "Ненецкий автономный округ" : 83,"Ханты-Мансийский Автономный округ - Югра автономный округ" : 86,
    "Чукотский автономный округ" : 87,"Ямало-Ненецкий автономный округ" : 89,"Крым республика" : 91,
    "Севастополь город" : 92,"Байконур город" : 99 }

REDUCTIONS = {
    'КР': ['КРАЙ','КРАЯ','КРАИ','КРАЮ','КРАЕ'],
    'РЕСП': ['РЕСПУБЛИКА','РЕСПУБЛИКУ','РЕСПУБЛИКИ','РЕСПУБЛИКОЙ','РЕСПУБЛИКЕ'],
    'Р': ['РАЙОНА','РАЙОНУ','РАЙОНЕ','РАЙОН','РАИОНА','РАИОНУ','РАИОНЕ','РАИОН','Р-НА','Р-НУ','Р-НЕ','Р-Н'],
    'ОБЛ': ['ОБЛАСТИ','ОБЛАСТЬЮ','ОБЛАСТЬ'],
    'АО': ['АВТОНОМНОГО ОКРУГА','АВТОНОМНЫМ ОКРУГОМ','АВТОНОМНОМУ ОКРУГУ','АВТОНОМНЫЙ ОКРУГ', 'АВТОНОМНОГО ОКР',
           'АВТОНОМНЫЙ ОКР','АВТОНОМНЫМ ОКР','АВТОНОМНОМУ ОКР','АВТ ОКР'],
    'ОУФМС': ['ОТДЕЛОМ УФМС','ОТДЕЛ УФМС','ОТДЕЛУ УФМС','ОТДЕЛА УФМС','ОТД УФМС','ОТДЕЛЕНИЕМ УФМС','ОТДЕЛЕНИЕ УФМС',
              'ОТДЕЛЕНИЮ УФМС','ОТДЕЛЕНИЯ УФМС'],
    'Г': ['ГОРОДА','ГОРОДУ','ГОРОДОМ','ГОРОДЕ','ГОРОД','ГОР'],
    'ОКР': ['ОКРУГА','ОКРУГУ','ОКРУГОМ','ОКРУГЕ','ОКРУГ'],
    '': ['#','№'],
    'МУН': ['МУНИЦИПАЛЬНЫМ','МУНИЦИПАЛЬНЫЙ','МУНИЦИПАЛЬНОГО','МУНИЦИПАЛЬНОМУ']
}

def chuvak(is_chuvak):
    if s(is_chuvak).split(' ')[0] == 'ЧУВАШСКАЯ':
        return 'ЧУВАШСКАЯ'
    elif s(is_chuvak).split(' ')[0] == 'САХА':
        return 'САХА'
    else:
        return is_chuvak

dbconfig_ops = read_config(filename='alfa.ini', section='SaturnOPS')
dbconn_ops = MySQLConnection(**dbconfig_ops)

dbconfig_fin = read_config(filename='alfa.ini', section='SaturnFIN')
dbconn_fin = MySQLConnection(**dbconfig_fin)

cursor = dbconn_ops.cursor()
sql_ops = 'SELECT cl.client_id, cl.p_surname, cl.p_name, cl.p_lastname, cl.email, ca.client_phone, cl.b_date, ' \
          'cl.p_region, cl.d_region, cl.p_district, cl.p_place, cl.p_subplace, cl.d_district, cl.d_place, ' \
          'cl.d_subplace, cl.gender, cl.b_country, cl.b_region, cl.b_district, cl.b_place, cl.p_seria, cl.p_number, ' \
          'cl.p_date, cl.p_police, cl.p_police_code, cl.`number` '\
          'FROM saturn_crm.clients AS cl LEFT JOIN saturn_crm.contracts AS co ON cl.client_id = co.client_id ' \
          'LEFT JOIN saturn_crm.callcenter AS ca ON ca.contract_id = co.id ' \
          'WHERE cl.subdomain_id = 2 AND co.inserted_code = 9375 AND co.external_status_callcenter_code = 4' #\
#          'AND co.status_code = 1 ' \
#          'AND co.exchanged = 0 AND co.id IS NOT NULL ORDER BY co.client_id, ca.updated_date DESC'

# 'AND ca.client_phone = 79241609997 ' \
# 'AND external_status_code = 0 ' \

    # cl.p_surname = "КУДРЯШОВ" AND
cursor.execute(sql_ops)
rows = cursor.fetchall()
headers = {}
for i, desc_ops in enumerate(cursor.description):
    headers[desc_ops[0]] = i
last_id = ''
tuples_fin = []
tuples_fins = []
tuples_ops = []
tuples_opses = []
tuples_ops_err = []
good_zayavka = 0
bad_zayavka = 0

for i, row in enumerate(rows):
    if last_id == row[headers['client_id']]:
        continue
    kladr_ok = True
    last_id = row[headers['client_id']]
    region_ch = 'd'
    region = chuvak(row[headers['d_region']])
    if not region:
        region_ch = 'd'
        kladr_ok = False
        region = row[headers['d_place']]
    if not region:
        region = chuvak(row[headers['p_region']])
        region_ch = 'p'
    if not region:
        region = row[headers['p_place']]
        kladr_ok = False
        region_ch = 'p'
    if not region:
        region = 'РЕГИОН НЕ УКАЗАН'
    region_id = -1
    for j, alfa_region in enumerate(ALFA_REGIONS):
        if alfa_region.upper().find(region) > -1:
            region_id = ALFA_REGIONS[alfa_region]
            break

    b_country = ''
    if lenl(row[headers['b_country']]) > 0:
        b_country = row[headers['b_country']]
    b_region = ''
    if lenl(row[headers['b_region']]) > 0:
        b_region = row[headers['b_region']]
    b_district = ''
    if lenl(row[headers['b_district']]) > 0:
        b_district = row[headers['b_district']]
    b_place = ''
    if lenl(row[headers['b_place']]) > 0:
        b_place = row[headers['b_place']]

    if b_country.upper().strip() == 'РОССИЯ' or b_country.upper().strip() == 'РФ':
        b_country = ''
    if len(b_place) > 35:
        birth_address = 'Сократить название места рождения до 35 симв не получилось: '
    elif len(b_place) + len(b_country) > 35:
        birth_address = b_place
    elif len(b_region) + len(b_place) + len(b_country) > 35:
        birth_address = b_country + b_place
    elif len(b_district) + len(b_region) + len(b_place) + len(b_country) > 35:
        birth_address = b_country + b_region + b_place
    elif len(b_district) + len(b_region) + len(b_place) + len(b_country) < 36 and \
         len(b_district) + len(b_region) + len(b_place) + len(b_country) > 0:
        birth_address = b_country + b_region + b_district + b_place
    else:
        birth_address = 'Не заполнено место рождения'

    p_police_old = row[headers['p_police']]
    p_police = row[headers['p_police']].replace('.',' ').replace(',',' ').replace('  ',' ').replace('  ',' ')
    p_police = p_police.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').upper()
    if len(p_police) > 70:
        for j, reduction in enumerate(REDUCTIONS):
            for change in REDUCTIONS[reduction]:
                p_police = p_police.replace(change,reduction)
                q=0

    if region_id == -1:
        bad_zayavka += 1
        if region == 'РЕГИОН НЕ УКАЗАН':
            print(row[headers['number']],'"' + row[headers['p_surname']], row[headers['p_name']], row[headers['p_lastname']] +
                  '"', row[headers['client_phone']], '""', '"Регион не указан"')
        elif not kladr_ok:
            print(row[headers['number']],'"' + row[headers['p_surname']], row[headers['p_name']], row[headers['p_lastname']] +
                  '"', row[headers['client_phone']], '"' + region + '"', '"Пересохраните КЛАДР"')
        else:
            print(row[headers['number']],'"' + row[headers['p_surname']], row[headers['p_name']], row[headers['p_lastname']] +
                  '"', row[headers['client_phone']], '"' + region + '"', '"Регион не участвует в программе"')
        tuples_ops_err.append((row[0],))
        continue
    if len(row[headers['p_surname']]) > 35 or len(row[headers['p_name']]) > 35 or len(row[headers['p_lastname']]) > 35:
        bad_zayavka += 1
        print(row[headers['number']],'"' + row[headers['p_surname']], row[headers['p_name']], row[headers['p_lastname']] +
                  '"', row[headers['client_phone']], '"' + region + '"', '"Длина Фамилии Имени или Отчества больше 35 символов"')
        tuples_ops_err.append((row[0],))
        continue
    if birth_address == 'Сократить название места рождения до 35 симв не получилось: ' \
                         or birth_address == 'Не заполнено место рождения':
        bad_zayavka += 1
        print(row[headers['number']],'"' + row[headers['p_surname']], row[headers['p_name']], row[headers['p_lastname']] +
              '"', row[headers['client_phone']], '"' + region + '"', '"',birth_address +
              b_country + b_region + b_district + b_place,'"')
        tuples_ops_err.append((row[0],))
        continue
    if len(p_police) > 70:
        err_police =  'Сократить название название подразделения до 70 симв не получилось: '+ p_police
        bad_zayavka += 1
        print(row[headers['number']],'"' + row[headers['p_surname']], row[headers['p_name']], row[headers['p_lastname']] +
                  '"', row[headers['client_phone']], '"' + region + '"', '"',err_police,'"')
        tuples_ops_err.append((row[0],))
        continue
    if not row[headers['p_surname']] or not row[headers['p_name']] or not row[headers['p_lastname']] \
            or lenl(row[headers['client_phone']]) == 0 or lenl(row[headers['b_date']]) == 0 \
            or lenl(row[headers['gender']]) == 0 or lenl(row[headers['p_seria']]) == 0 \
            or lenl(row[headers['p_number']]) == 0 or lenl(row[headers['p_date']]) == 0 \
            or not p_police or lenl(row[headers['p_police_code']]) == 0 :
        bad_zayavka += 1
        print(row[headers['number']],'"' + row[headers['p_surname']], row[headers['p_name']], row[headers['p_lastname']] +
                  '"', row[headers['client_phone']], '"' + region + '"','"Отсутствует обязательное поле"')
        tuples_ops_err.append((row[0],))
        continue

    tuples_fin.append((row[headers['client_id']], row[headers['p_surname']], row[headers['p_name']],
                       row[headers['p_lastname']], row[headers['email']], row[headers['client_phone']],
                       row[headers['b_date']], region_id, datetime.datetime.now(), 3090, 0,
                       row[headers['gender']], birth_address, row[headers['p_seria']], row[headers['p_number']],
                       row[headers['p_date']], p_police, row[headers['p_police_code']]))
    tuples_ops.append((row[0],))
    good_zayavka += 1
    if len(tuples_fin) > 999:
        tuples_fins.append(tuples_fin)
        tuples_fin = []
    if len(tuples_ops) > 999:
        tuples_opses.append(tuples_ops)
        tuples_ops = []
tuples_fins.append(tuples_fin)
tuples_opses.append(tuples_ops)

print('\nОбработано: ', bad_zayavka + good_zayavka,'   загружено: ', good_zayavka, '   ошибки: ', bad_zayavka)

if len(tuples_fin) > 0:
    for i, t_fin in enumerate(tuples_fins):
        cursor_fin = dbconn_fin.cursor()
        sql_fin = 'INSERT INTO saturn_fin.alfabank_products(remote_id, last_name, first_name, middle_name, ' \
                  'e_mail, phone, birth_date, w_region, inserted_date, inserted_code, status_code, ' \
                  'gender, birth_address, p_seria, p_number, p_date, p_police, p_police_code ' \
                  ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor_fin.executemany(sql_fin, t_fin)
        cursor_ops = dbconn_ops.cursor()                        # Статус "Загружено" (Бумага принята)
        sql_ops = 'UPDATE saturn_crm.contracts SET external_status_callcenter_code = 1 WHERE client_id = %s'
        cursor_ops.executemany(sql_ops, tuples_opses[i])
        dbconn_fin.commit()
        dbconn_ops.commit()
#if len(tuples_ops_err) > 0:
#    cursor_ops = dbconn_ops.cursor()                        # Статус "Ошибка"
#    sql_ops = 'UPDATE saturn_crm.contracts SET exchanged = 0 WHERE client_id = %s'
#    cursor_ops.executemany(sql_ops, tuples_ops_err)
#    dbconn_ops.commit()

dbconn_fin.close()
dbconn_ops.close()

# -*- coding: utf-8 -*-
# Общие переменые и процедуры проекта alfa

import json, requests
from datetime import datetime

# DRIVER_PATH = 'drivers/chromedriver.exe'
DRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
LOG_PATH = 'logs/'
LOG_FILE = 'rabbit_transfer.log'
BAD_TRANSACTION_LOG_FILE = 'rabbit_bad_transactions.log'
MAX_PROCESSES = 10
CYCLES_ORDERITY = 1 # Количество попыток заполнения заявки
ALOADER_TIMEOUT = 31 # минут - время жизни aloader'а после заполнения заявки

# список очерёдности
orderity = [
    {'alfa': 'Фамилия', 'SQL': ['passport_lastname'], 'pre-click': '//SPAN[@class="input__top"][text()="Фамилия"]/..',
     'input': '//INPUT[@class="input__control"][@name="lastName"]', 'post-click': '//DIV[contains(@class,"landing-page")]'},
    {'alfa': 'Имя', 'SQL': ['passport_name'], 'pre-click': '//SPAN[@class="input__top"][text()="Имя"]/..',
     'input': '//INPUT[@class="input__control"][@name="firstName"]', 'post-click': '//DIV[contains(@class,"landing-page")]'},
    {'alfa': 'Отчество', 'SQL': ['passport_middlename'], 'pre-click': '//SPAN[@class="input__top"][text()="Отчество"]/..',
     'input': '//INPUT[@class="input__control"][@name="middleName"]', 'post-click': '//DIV[contains(@class,"landing-page")]'},
    {'alfa': 'Пол', 'SQL': ['gender'],
     'click-text': '//SPAN[@class="tag-button__text"][text()="',
     'post-click': '//DIV[contains(@class,"landing-page")]'},
    {'alfa': 'Мобильный телефон', 'SQL': ['personal_phone'],
     'pre-click': '//SPAN[@class="input__top"][text()="Мобильный телефон"]/..',
     'input-tel': '//INPUT[@class="input__control"][@name="phone"]', 'post-click': '//DIV[contains(@class,"landing-page")]'},
    {'alfa': 'Электронная почта', 'SQL': ['e_mail'], 'pre-click': '//SPAN[@class="input__top"][text()="Электронная почта"]/..',
     'input': '//INPUT[@class="input__control"][@name="email"]', 'post-click': '//DIV[contains(@class,"landing-page")]'},
    {'alfa': 'Регион работы', 'SQL': ['current_address_region'], 'pre-click': '//INPUT[@placeholder="Регион работы"]',
     'click-text-up': '//SPAN[@class="menu-item__control"][text()="', 'post-click': '//DIV[contains(@class,"landing-page")]'},
    {'alfa': 'Продолжить', 'click': '//SPAN[@class="button__text"][text()="Продолжить"]', 'loaded': '20%'},
    #------------------------------------------------ страница 2 ---------------------
    {'alfa': 'Серия', 'SQL': ['passport_seria'], 'input': '//INPUT[@class="input__control"][@name="passportSeries"]',
     'post-click': '//H3'},
    {'alfa': 'Номер', 'SQL': ['passport_number'], 'input': '//INPUT[@class="input__control"][@name="passportNumber"]',
     'post-click': '//H3'},
    {'alfa': 'Дата выдачи', 'SQL': ['passport_date'],
     'pre-click': '//SPAN[@class="input__top"][text()="Дата выдачи"]/..',
     'input': '//INPUT[@class="input__control"][@name="passportIssuedDate"]',
     'post-click': '//H3'},
    {'alfa': 'Код подразделения', 'SQL': ['passport_police_code'],
     'pre-click': '//SPAN[@class="input__top"][text()="Код подразделения"]/..',
     'input': '//INPUT[@class="input__control"][@name="passportIssuedCode"]',
     'post-click': '//H3'},
    {'alfa': 'Кем выдан', 'SQL': ['passport_police'], 'post-wait': 1,
     'check-until': '//TEXTAREA[@class="textarea__control"][@name="passportIssuedBy"]',
     'check-value': '//TEXTAREA[@class="textarea__control"][@name="passportIssuedBy"]',
     'input': '//TEXTAREA[@class="textarea__control"][@name="passportIssuedBy"]',
     'post-click': '//H3'},
    {'alfa': 'Дата рождения', 'SQL': ['birth_date'],'pre-wait': 1, 'post-wait': 1,
     'pre-click': '//SPAN[@class="input__top"][text()="Дата рождения"]/..',
     'input': '//INPUT[@class="input__control"][@name="birthDate"]',
     'post-click': '//H3'},
    {'alfa': 'Место рождения', 'SQL': ['passport_birth_address'],
     'pre-click': '//SPAN[@class="input__top"][text()="Место рождения"]/..',
     'input': '//INPUT[@class="input__control"][@name="passportBirthPlace"]',
     'post-click': '//H3'},
    {'alfa': 'Регион регистрации', 'SQL': ['registration_region'],
     'pre-click': '//SPAN[@class="input__top"][text()="Регион регистрации"]/..',
     'click-text-up': '//SPAN[@class="menu-item__control"][text()="',
     'post-click': '//H3'},
    {'alfa': 'Продолжить', 'click': '//SPAN[@class="button__text"][text()="Продолжить"]', 'loaded': '40%'},
    #------------------------------------------------ страница 3 ---------------------
    {'alfa': 'Название организации', 'SQL': ['work_organization'],
     'pre-click': '//SPAN[@class="input__top"][text()="Название организации"]/..',
     'input': '//INPUT[@class="input__control"][@name="organizationName"]',
     'post-click': '//H3'},
    {'alfa': 'ИНН организации', 'SQL': ['work_organization_inn'],
     'pre-click': '//SPAN[@class="input__top"][text()="ИНН организации"]/..',
     'input': '//INPUT[@class="input__control"][@name="organizationInn"]',
     'post-click': '//H3'},
    {'alfa': 'Должность', 'SQL': ['work_position'],
     'pre-click': '//SPAN[@class="input__top"][text()="Должность"]/..',
     'input': '//INPUT[@class="input__control"][@name="workPost"]',
     'post-click': '//H3'},
    {'alfa': 'Рабочий телефон', 'SQL': ['work_contact_phone'],
     'pre-click': '//SPAN[@class="input__top"][text()="Рабочий телефон"]/..',
     'input-tel': '//INPUT[@class="input__control"][@name="workPhone"]',
     'post-click': '//H3'},
    {'alfa': 'Размер заработной платы по основному месту работы', 'SQL': ['work_salary'],
     'pre-click': '//SPAN[@class="input__top"][text()="Размер заработной платы по основному месту работы"]/..',
     'input': '//INPUT[@class="input__control"][@name="mainIncome"]',
     'post-click': '//H3'},
    {'alfa': 'Образование', 'SQL': ['education'],
     'pre-click': '//SPAN[@class="select__top"][text()="Образование"]/..',
     'click': '//SPAN[@class="menu-item__control"][text()="Высшее"]/..',
     'post-click': '//H3'},
    {'alfa': 'Продолжить', 'click': '//SPAN[@class="button__text"][text()="Продолжить"]', 'loaded': '60%'},
    # ------------------------------------------------ страница 4 ---------------------
    {'alfa': 'Желаемый кредитный лимит', 'SQL': ['credit_limit'],
     'pre-click': '//SPAN[@class="input__top"][text()="Желаемый кредитный лимит"]/..',
     'input': '//INPUT[@class="input__control"][@name="creditLimit"]',
     'post-click': '//H3'},
    {'alfa': 'Второй документ, удостоверяющий личность', 'SQL': ['second_document'],
     'check-absence': '//DIV[contains(@class,"part_hidden")]//SPAN[@class="select__top"]'
                      '[text()="Второй документ, удостоверяющий личность"]',
     'pre-click': '//SPAN[@class="select__top"][text()="Второй документ, удостоверяющий личность"]/..',
     'check-with-name': '//SPAN[@class="menu-item__control"]',
     'click-text-up': '//SPAN[@class="menu-item__control"][text()="',
     'post-click': '//H3'},
    {'alfa': 'Документ, подтверждающий доход', 'SQL': ['salary_confirmation'],
     'check-absence': '//DIV[contains(@class,"part_hidden")]//SPAN[@class="select__top"]'
                      '[text()="Документ, подтверждающий доход"]',
     'pre-click': '//SPAN[@class="select__top"][text()="Документ, подтверждающий доход"]/..',
     'check-with-name': '//SPAN[@class="menu-item__control"]',
     'click-text-up': '//SPAN[@class="menu-item__control"][text()="',
     'post-click': '//H3'},
    {'alfa': 'Продолжить', 'click': '//SPAN[@class="button__text"][text()="Продолжить"]', 'loaded': '80%'},
    # ------------------------------------------------ страница 5 ---------------------
    {'alfa': 'Фамилия контактного лица', 'SQL': ['reference_lastname'],
     'pre-click': '//SPAN[@class="input__top"][text()="Фамилия контактного лица"]/..',
     'input': '//INPUT[@class="input__control"][@name="contactLastName"]',
     'post-click': '//H3'},
    {'alfa': 'Имя контактного лица', 'SQL': ['reference_name'],
     'pre-click': '//SPAN[@class="input__top"][text()="Имя контактного лица"]/..',
     'input': '//INPUT[@class="input__control"][@name="contactFirstName"]',
     'post-click': '//H3'},
    {'alfa': 'Отчество контактного лица', 'SQL': ['reference_middlename'],
     'pre-click': '//SPAN[@class="input__top"][text()="Отчество контактного лица"]/..',
     'input': '//INPUT[@class="input__control"][@name="contactMiddleName"]',
     'post-click': '//H3'},
    {'alfa': 'Моб. телефон контактного лица', 'SQL': ['reference_contact_phone'],
     'pre-click': '//SPAN[@class="input__top"][text()="Моб. телефон контактного лица"]/..',
     'input-tel': '//INPUT[@class="input__control"][@name="contactMobilePhone"]',
     'post-click': '//H3'},
    {'alfa': 'Кодовое слово', 'SQL': ['secret_word'],
     'pre-click': '//SPAN[@class="input__top"][text()="Кодовое слово"]/..',
     'input': '//INPUT[@class="input__control"][@name="codeWord"]',
     'post-click': '//H3'},
    {'alfa': 'Город получения карты', 'SQL': ['city'],
     'pre-click': '//SPAN[@class="input__top"][text()="Город получения карты"]/..',
     'click-text-up': '//SPAN[@class="menu-item__control"][text()="',
     'post-click': '//H3'},
    {'alfa': 'Выберите город и способ получения карты', 'check-delivery':'//SPAN[text()="Курьером бесплатно"]',
     'click': '//SPAN[@class="title"][text()="Курьером бесплатно"]/..'},
    {'alfa': 'Как быстро вам нужна карта?', 'SQL': ['delivery_time'],
     'radio-select': ['//SPAN[@class="radio__title"][text()="Сегодня"]/..',
                      '//SPAN[@class="radio__title"][text()="Через 1-3 дня"]/..'],
     'radio-select-input': ['Сегодня (Без фамилии и имени на карте)', 'Через 1-3 дня (С фамилией и именем на карте)']},
    {'alfa': 'Разрешаю мне звонить с 22:00 до 8:00 (в ночное время)', 'SQL': ['allow_night_calls'],
     'check-until': '//SPAN[text()="Разрешаю мне звонить с 22:00 до 8:00 (в ночное время)"]',
     'checkbox': '//SPAN[text()="Разрешаю мне звонить с 22:00 до 8:00 (в ночное время)"]', 'loaded': '100%'},
    # ------------------------------------------------ Отправить заявку ---------------------
    {'alfa': 'Отправить заявку', 'click': '//SPAN[@class="button__text"][text()="Отправить заявку"]'},

]
smsity = {
    'Изменить номер телефона': '//SPAN[@class="button__text"][text()="Изменить номер телефона"]',
    'Ждет СМС': '//P[contains(@class,"confirmation__text")][contains(text(),"сек")]',
    'Ждет запроса на СМС': '//SPAN[text()="Запросить пароль повторно"]',
    'Запросить пароль повторно': '//SPAN[@class="button__text"][text()="Запросить пароль повторно"]/../..',
    'Ввести СМС': '//SPAN[contains(@class,"confirmation-modal__input")]//INPUT[@class="input__control"]'
}


# поля, на которые надо кликать Отправить заявку
clicktity = {
'Вход' : {'t': 'x', 's': '//DIV[@class="hh left"][text()="Вход"]' , 'SQL': "1"}, # Кнопка Вход
'Фамилия' : {'t': 'x', 's': '//SPAN[@class="input__top"][text()="Фамилия"]/..' , 'SQL': "1"}, # Фамилия
'Ошибки' : {'t': 'x', 's': '//SPAN[contains(@class,"input_invalid")]//SPAN[@class="input__sub"]' , 'SQL': "1", 'a': 'text'}, #

'cMob' : {'t': 'x', 's': '//[@class="mobile_verified"]' , 'SQL': "1"}, # Звонок на этот мобильный телефон (вычисляемое)
'cIndREGAmn' : {'t': 'x', 's': '//[@class="amnesia_reg"]' , 'SQL': "IF(a.p_postalcode=0 OR a.p_postalcode=111111,1,0)"}, # Индекс =рег - не помню
'cAddrFACTtoo' : {'t': 'x', 's': '//LABEL[@for="reg_addr_is_home_addr"]' , 'SQL': "0"}, #ok Адрес проживания такой же?
'cIndFACTAmn' : {'t': 'x', 's': '//[@class="amnesia_home"]' , 'SQL': "IF(a.d_postalcode=0 OR a.d_postalcode=111111,1,0)"}, # Индекс =прож - не помню
'cNoStPhone' : {'t': 'x', 's': '//[@class="no_home_phone"]' , 'SQL': "IF(b.landline_phone<70000000000 OR b.landline_phone IS null,1,0)"}, # Нет стац. телефона
'cBisUnOfficial' : {'t': 'x', 's': '//SPAN[text()="Неофициальный бизнес"]' , 'SQL': "b.unofficial_employment_code"}, # Свой бизнес не официальный?
'cIndWORKAmn' : {'t': 'x', 's': '//[@class="amnesia_work"]' , 'SQL': "IF(b.w_postalcode=0 OR b.w_postalcode=111111,1,0)"}, # Индекс =раб - не помню
'cAddrWORKtoo' : {'t': 'x', 's': '//LABEL[@for="same_reg_home_org"]' , 'SQL': "0"}, #ok Адрес бизнеса такой же как рег?
'ПодтвМобТел' : {'t': 'x', 's': '//LABEL[@for="phone_mobile_check"]//SPAN[text()="Проверено"]' , 'SQL': "1"},
'ПодтвФамилии' : {'t': 'x', 's': '//LABEL[@for="surname_verified"]//SPAN[text()="Проверено"]' , 'SQL': "1"},
'ПодтвИмени' : {'t': 'x', 's': '//LABEL[@for="name_verified"]//SPAN[text()="Проверено"]' , 'SQL': "1"},
'ПодтвОтчества' : {'t': 'x', 's': '//LABEL[@for="patronymic_verified"]//SPAN[text()="Проверено"]' , 'SQL': "1"},
'Оформить' : {'t': 'x', 's': '//BUTTON[@type="button"]//SPAN[text()="Оформить"]/..' , 'SQL': "1"},
'Загружено?' : {'t': 'x', 's': '//H1[text()="Спасибо за предоставленную информацию"]' , 'SQL': "1"},
'СледующаяЗаявка' : {'t': 'x', 's': '//INPUT[@value="Заполнить новую заявку"]' , 'SQL': "1"},
'ПроверкаИндекса' : {'t': 'x', 's': '//DIV[text()="Несуществующий индекс"]' , 'SQL': "1"},
'НетКАСКО' : {'t': 'x', 's': '//SPAN[text()="Нет полиса КАСКО"]',
       'SQL': "IF((b.car_insurance_expiration_date IS NOT NULL) AND (b.car_insurance_expiration_date > NOW()),0,1)"},
'ЕстьЗагранПаспорт' : {'t': 'x', 's': '//SPAN[text()="Есть заграничный паспорт"]' ,
                       'SQL': "IF(b.travel_information_code>0,1,0)"},
'ПредоставлюЗагранПаспорт' : {'t': 'x', 's': '//SPAN[text()="Предоставлю на встрече заграничный паспорт"]',
                              'SQL': "IF(b.travel_information_code>0,1,0)"},
'Ошибки-старые' : {'t': 'x', 's': '//DIV[@class="ui-form-field-error-message ui-form-field-error-message_ui-form"]', 'a':'text', 'SQL': "1"},
}

def writelog(file, click_id, message, pid=0, date_time=datetime.now()):
    if not pid:
        pid_str = ' NONE '
    elif pid == 1:
        pid_str = ' MAIN '
    else:
        pid_str = str(pid)
    file.write(click_id + '(' + pid_str + ') ' + date_time.strftime("%d-%H:%M:%S") + '>' + message + '\n')

def post_status(url, click_id, status, message, log, bad_log):
    statuses = {
        "1": "Заполняет анкету",
        "2": "Ждет СМС",
        "3": "Ждет запроса на СМС",
        "4": "Успешное завершение",
        "5": "Ошибка",
        "6": "Завис",
        "7": "Перегрузка (слишком много aloader'ов)",
        "8": "Невозможно ввести SMS, нет такого aloader'а",
        "9": "Был убит",
       "10": "Таймаут, нет правильной СМС",
       "11": "Запрос информации"
    }
    field = json.dumps({'status': int(status), 'message': message}).encode('utf8')
    res = requests.post(url + click_id, data=field, headers={'content-type': 'application/json'})
    if res.status_code == 200:
        writelog(log, click_id, 'В postAPI отправлен статус "' + statuses[str(status)] + '", ответ - '
                 + str(res.status_code))
    else:
        writelog(log, click_id, 'Ошибка отправки статуса "' + statuses[str(status)] + '" в postAPI, ответ - '
                 + str(res.status_code))
        writelog(bad_log, click_id, 'Ошибка отправки статуса "' + statuses[str(status)] + '" в postAPI, ответ - '
                 + str(res.status_code))

# -*- coding: utf-8 -*-
# Общие переменые и процедуры проекта WebZagrTink

clicktity = {
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
'Ошибки' : {'t': 'x', 's': '//DIV[@class="ui-form-field-error-message ui-form-field-error-message_ui-form"]', 'a':'text', 'SQL': "1"},
}


inputtity = {
'iId' : {'t': 'x', 's': '//[@class="id"]', 'SQL': "a.client_id"}, # Поле id для update b.loaded
'Фамилия' : {'t': 'x', 's': '//INPUT[@type="text"][@name="surname"]', 'SQL': "a.p_surname"}, # Фамилия
'Имя' : {'t': 'x', 's': '//INPUT[@type="text"][@name="name"]', 'SQL': "a.p_name"}, # Имя
'Отчество' : {'t': 'x', 's': '//INPUT[@type="text"][@name="patronymic"]', 'SQL': "a.p_lastname"}, # Отчество
'МобТелефон' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="phone_mobile"]', 'SQL': "b.phone_personal_mobile"}, # Мобильный телефон
'СНИЛС' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="social_security_no"]', 'SQL': "a.number"},
'Email' : {'t': 'x', 's': '//INPUT[@type="text"][@name="email"]', 'SQL': "a.email"}, # Электронная почта
'СерияНомер' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="id_code_number"]' , 'SQL': "CONCAT_WS('',a.p_seria,a.p_number)"}, # Паспорт (номер и серия)
'КемВыдан' : {'t': 'x', 's': '//TEXTAREA[@name="passport_who_given"]' , 'SQL': "a.p_police"}, # Кто выдал
'ДатаВыдачи' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="passport_date_given"]' , 'SQL': "DATE_FORMAT(a.p_date,'%d%m%Y')"}, # Дата выдачи
'КодПодразд' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="id_division_code"]' , 'SQL': "a.p_police_code"}, # Код подразделения
'ДатаРождения' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="birthdate"]' , 'SQL': "DATE_FORMAT(a.b_date,'%d%m%Y')"}, # Дата рождения
'МестоРождения' : {'t': 'x', 's': '//INPUT[@type="text"][@name="place_of_birth"]'
              , 'SQL': "CONCAT_WS(' ', a.b_country,a.b_region,a.b_district,a.b_place)"}, # Место рождения
'МаркаАвто' : {'t': 'x', 's': '//INPUT[@type="text"][@name="car_producer"]' , 'SQL': "b.car_brand"},
'МодельАвто' : {'t': 'x', 's': '//INPUT[@type="text"][@name="car_model"]' , 'SQL': "b.car_model"},
'ДатаКАСКОАвто' : {'t': 'x', 's': '//INPUT[@type="text"][@name="car_model"]' , 'SQL': "DATE_FORMAT(b.car_insurance_expiration_date,'%d%m%Y')"},

'ИндексФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="tel"][@name="postal_code"]', 'SQL': "a.d_postalcode"}, # Индекс =факт
'РегионФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="place"]' ,
                'SQL': "CONCAT_WS(' ',a.d_region,a.d_region_type)"}, # Регион =факт
'РегионФАКТзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="place"]', 'a':'value', 'SQL': "1"},
'РайонФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="area"]' ,
                    'SQL': "CONCAT_WS(' ',a.d_district_type,a.d_district)"}, # Район =факт
'ГородФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="area"]' ,
                    'SQL': "CONCAT_WS(' ',a.d_place_type,a.d_place)"}, # Город =факт
'НасПунктФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="city"]',
                 'SQL': "CONCAT_WS(' ',a.d_subplace_type,a.d_subplace)"}, # Населенный пункт =факт
'РайонФАКТзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="area"]' , 'a':'value', 'SQL': "1"},
'НасПунктФАКТзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="city"]', 'a': 'value', 'SQL': "1"},
'УлицаФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="street"]',
              'SQL': "CONCAT_WS(' ',a.d_street_type,a.d_street)"},
'УлицаФАКТзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="street"]', 'a': 'value', 'SQL': "1"},
'ДомФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="building"]', 'SQL': "a.d_building"}, # Дом =факт
'КорпусФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="corpus"]' , 'SQL': "a.d_corpus"}, # Корпус =факт
'СтроениеФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="stroenie"]', 'SQL': ""}, # Строение =факт
'КвартираФАКТ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][2]//INPUT[@type="text"][@name="flat"]', 'SQL': "a.d_flat"}, # Квартира =факт
'ИндексРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="tel"][@name="postal_code"]', 'SQL': "a.p_postalcode"}, # Индекс =рег
'РегионРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="place"]',
               'SQL': "CONCAT_WS(' ',a.p_region,a.p_region_type)"}, # Регион =рег
'РегионРЕГзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="place"]', 'a': 'value', 'SQL': "1" }, # Регион =рег
'РайонРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="area"]',
                    'SQL': "CONCAT_WS(' ',a.p_district_type,a.p_district)"}, # Район =рег
'ГородРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="area"]',
                    'SQL': "CONCAT_WS(' ',a.p_place_type,a.p_place)"}, # Город =рег
'НасПунктРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="city"]',
                 'SQL': "CONCAT_WS(' ',a.p_subplace_type,a.p_subplace)"}, # Населенный пункт =рег
'РайонРЕГзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="area"]', 'a': 'value', 'SQL': "1" },
'НасПунктРЕГзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="city"]', 'a': 'value', 'SQL': "1"},
'УлицаРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="street"]',
              'SQL': "CONCAT_WS(' ',a.p_street_type,a.p_street)"}, # Улица =рег
'УлицаРЕГзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="street"]', 'a': 'value', 'SQL': "1"},
'ДомРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="building"]', 'SQL': "a.p_building"}, # Дом =рег
'КорпусРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="corpus"]' , 'SQL': "a.p_corpus"}, # Корпус =рег
'СтроениеРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="stroenie"]' , 'SQL': ""}, # Строение =рег
'КвартираРЕГ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][1]//INPUT[@type="text"][@name="flat"]' , 'SQL': "a.p_flat"}, # Квартира =рег
'ДопТелефон' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="additional_phone_home"]', 'SQL': "b.additional_phone"}, # Дополнительный телефон
'ИмяДопТелефон' : {'t': 'x', 's': '//INPUT[@type="text"][@name="additional_phone_home_comment"]',
                   'SQL': "b.additional_phone_person"},
'НазвФирмы' : {'t': 'x', 's': '//TEXTAREA[@name="work_name"]' , 'SQL': "b.employment_organization"}, # Наименование организации
'НазвДолжности' : {'t': 'x', 's': '//INPUT[@name="work_position_text"]' , 'SQL': "b.employment_position"}, # Название должности !!!!!ПОКА НЕТ!!!!
'ТелефонРАБ' : {'t': 'x', 's': '//INPUT[@name="phone_work"]' , 'SQL': "b.employment_phone"}, # Рабочий телефон
'ИндексРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="tel"][@name="postal_code"]', 'SQL': "b.w_postalcode"}, # Индекс =раб
'РегионРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="place"]' ,
               'SQL': "CONCAT_WS(' ',b.w_region,b.w_region_type)"}, # Регион =раб
'РегионРАБзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="place"]', 'a': 'value', 'SQL': "1"},
'РайонРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="area"]' ,
                    'SQL': "CONCAT_WS(' ',b.w_district_type,b.w_district)"}, # Район =раб
'РайонРАБзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="area"]', 'a': 'value', 'SQL': "1"},
'ГородРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="area"]' ,
                    'SQL': "CONCAT_WS(' ',b.w_place_type,b.w_place)"}, # Город =раб
'НасПунктРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="city"]' ,
                 'SQL': "CONCAT_WS(' ',b.w_subplace_type,b.w_subplace)"}, # Населенный пункт =раб
'НасПунктРАБзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="city"]', 'a': 'value', 'SQL': "1"},
'УлицаРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="street"]' ,
              'SQL': "CONCAT_WS(' ',b.w_street_type,b.w_street)"}, # Улица =раб
'УлицаРАБзнач' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="street"]', 'a': 'value', 'SQL': "1"},
'ДомРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="building"]' , 'SQL': "b.w_building"}, # Дом =раб
'КорпусРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="corpus"]' , 'SQL': "b.w_corpus"}, # Корпус =раб
'СтроениеРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="stroenie"]' , 'SQL': ""}, # Строение =раб
'НомОфисаРАБ' : {'t': 'x', 's': '//DIV[@class="ui-kladr"][3]//INPUT[@type="text"][@name="flat"]' , 'SQL': "b.w_flat"}, # Номер офиса =раб
'НеРаботаю-Другое' : {'t': 'x', 's': '//INPUT[@name="notwork_other_text"]' , 'SQL': "b.unemployment_other"}, # Не работаю - другое
'ПерсДоход' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="income_individual"]' , 'SQL': "b.personal_income"}, # Персональный доход
'КвартПлата' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="expenses_amount"]' , 'SQL': "b.flat_payment"}, # Сумма аренды квартиры
'ПлатежиПоКредитам' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="expenses_amount"]' , 'SQL': "b.banks_payment"}, # ССумма платежей по тек.кредитам в др.банках
'КредЛимит' : {'t': 'x', 's': '//INPUT[@type="tel"][@name="desired_credit_limit"]', 'SQL': "b.want_amount"}, # Кредитный лимит
'ЩелчокДляСброса' : {'t': 'x', 's': '//DIV[@class="app-form-nav-container_static"]', 'SQL': "1"},
#'СтацТелефон' : {'t': 'x', 's': '//[@class="phone_home"]' , 'SQL': "b.landline_phone-70000000000"}, # Стационарный телефон по месту проживания или регистрации
}

selectity = {
'ТипЗанятости' : {'t': 'x', 's': '//SELECT[@name="employment_type"]/..', 'SQL': "employment_status_code"},
'ТипНезанятости' : {'t': 'x', 's': "not_work", 'SQL': "unemployment_code"}, # Если не работаю то Кем ПРОВЕРИТЬ ИЗМЕНЕНИЯ !!!!!
'Должность' : {'t': 'x', 's': '//SPAN[text()="Тип должности"]', 'SQL': "b.employment_position_code"}, # Если работаю то Должность
'Стаж' : {'t': 'x', 's': '//SPAN[text()="Стаж работы в организации"]/../../..' , 'SQL': "b.employment_experience"}, # Стаж работы (тип)
'ВладелецДопТелефона' : {'t': 'x', 's': '//SELECT[@name="additional_phone_home_type"]/..',
                         'SQL': "b.additional_phone_owner"},
'ПлатежиКредитные' : {'t': 'x', 's': '//SELECT[@name="liability_n_w_amount__dbl"]/..' , 'SQL': "b.current_payments_code"},
'КредитнаяИстория' : {'t': 'x', 's': '//SELECT[@name="credit_history"]/..', 'SQL': "b.status_credit_history_code"}, # Какая кредитная история
'Образование' : {'t': 'x', 's': '//SELECT[@name="education"]/..'    , 'SQL': "b.status_education_code"}, # Образование
'СемейноеПоложение' : {'t': 'x', 's': '//SELECT[@name="marital_status"]/..', 'SQL': "b.status_marital_code"}, # Семейное положение
'Автомобиль' : {'t': 'x', 's': '//SELECT[@name="asset_foreign_vehicle_flag"]/..', 'SQL': "b.status_car_code"}, # Автомобиль
'ГодАвто' : {'t': 'x', 's': '//SPAN[text()="Год выпуска"]/../../../..' , 'SQL': "b.car_production_year"},
'ЧастоЗагран' : {'t': 'x', 's': '//SELECT[@name="visit_foreign_country_frequency"]/..' , 'SQL': "b.travel_information_code"},

#'ПрПолисКАСКО' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[16]'   , 'SQL': "auto_kasko_attachment_id"}, # Полис страхования КАСКО
#'ПрСНИЛС' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[18]'   , 'SQL': "number_attachment_id"}, # Предоставит СНИЛС
'ПрЗагранпаспорт' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[10]'   , 'SQL': "international_passport_attachment_id"}, # Предоставит Загранпаспорт
'СкДетей' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[3]'    , 'SQL': "status_childs_code"}, # Количество детей
'ПросрочкиПоКредитам' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[8]'    , 'SQL': "status_credit_delay_code"}, # Просрочки по текущим кредитам
'ПрВодительскоеУд' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[9]'    , 'SQL': "driver_card_attachment_id"}, # Предоставит вод.удостоверение
'ПрПенсионноеУд' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[11]'   , 'SQL': "pensioner_card_attachment_id"}, # Предоставит Пенс.удостоверение
'ПрУдОфицера' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[12]'   , 'SQL': "identity_card_mvd_attachment_id"}, # Предоставит Удост.офицера МВД
'ПрВоенныйБилет' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[13]'   , 'SQL': "military_card_attachment_id"}, # Предоставит Военный билет
'ПрСвРегТС' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[14]'   , 'SQL': "auto_reg_attachment_id"}, # Cвидетельство регистрации ТС
'ПрОригПТС' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[15]'   , 'SQL': "auto_pts_attachment_id"}, # Оригинал ПТС
'ПрПолисОСАГО' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[17]'   , 'SQL': "auto_osago_attachment_id"}, # Полис ОСАГО
'ПрИНН' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[19]'   , 'SQL': "inn_attachment_id"}, # Предоставит ИНН
'Пр2НДФЛ' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[20]'   , 'SQL': "has_2NDFL"}, # Предоставит 2 НДФЛ
'ПрСправкуОДоходах' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[21]'   , 'SQL': "has_income_report"}, # Предоставит Справку о доходах
}

select_selectity = {
'ТипЗанятости' : [{'t': 'x', 's': '//SPAN[text()="Работаю в организации"]', 'txt': 'Работаю в организации'},
                  {'t': 'x', 's': '//SPAN[text()="Собственный бизнес"]', 'txt': 'Собственный бизнес'},
                  {'t': 'x', 's': '//SPAN[text()="Не работаю"]', 'txt': 'Не работаю'}],
#'ТипЗанятости' : [{'t': 'x', 's': '//UL[@class="ui-select__slider ui-select__slider_open"]'
#                                  '//SPAN[text()="Работаю в организации"]', 'txt': 'Работаю в организации'},
#                  {'t': 'x', 's': '//UL[@class="ui-select__slider ui-select__slider_open"]'
#                                  '//SPAN[text()="Собственный бизнес"]', 'txt': 'Собственный бизнес'},
#                  {'t': 'x', 's': '//UL[@class="ui-select__slider ui-select__slider_open"]'
#                                  '//SPAN[text()="Не работаю"]', 'txt': 'Не работаю'}],
'ТипНезанятости' : [{'t': 'x', 's': '//DIV[text()="По возрасту/стажу работы"]', 'txt': 'По возрасту/стажу работы'}, # Если не работаю то почему
                    {'t': 'x', 's': '//DIV[text()="По инвалидности"]', 'txt': 'По инвалидности'},
                    {'t': 'x', 's': '//DIV[text()="Ищу работу"]', 'txt': 'Ищу работу'},
                    {'t': 'x', 's': '//DIV[text()="Содержит муж/жена"]', 'txt': 'Содержит муж/жена'},
                    {'t': 'x', 's': '//DIV[text()="Другое"]', 'txt': 'Другое'}],
'Должность' : [{'t': 'x', 's': '//SELECT[@name="work_position"]/../..//SPAN[text()="Генеральный директор"]',
                'txt': 'Генеральный директор'},
               {'t': 'x', 's': '//SELECT[@name="work_position"]/../..//SPAN[text()="Руководитель"]',
                'txt': 'Руководитель'},
               {'t': 'x', 's': '//SELECT[@name="work_position"]/../..//SPAN[text()="Специалист"]',
                'txt': 'Специалист'},
               {'t': 'x', 's': '//SELECT[@name="work_position"]/../..//SPAN[text()="Обсл. персонал"]',
                'txt': 'Обсл. персонал'},
               {'t': 'x', 's': '//SELECT[@name="work_position"]/../..//SPAN[text()="Рабочий"]',
                'txt': 'Рабочий'}],
'Стаж' : [{'t': 'x', 's': '//SPAN[text()="6 месяцев и меньше"]', 'txt': '6 месяцев и меньше'},
          {'t': 'x', 's': '//SPAN[text()="0,5-3 года"]', 'txt': '0,5-3 года'},
          {'t': 'x', 's': '//SPAN[text()="3-5 лет"]', 'txt': '3-5 лет'},
          {'t': 'x', 's': '//SPAN[text()="5-7 лет"]', 'txt': '5-7 лет'},
          {'t': 'x', 's': '//SPAN[text()="7 и более лет"]', 'txt': '7 и более лет'},],
'ВладелецДопТелефона' : [{'t': 'x', 's': '//SPAN[text()="Мой номер"]','txt':'Мой номер'},
                         {'t': 'x', 's': '//SPAN[text()="Номер родственника"]', 'txt': 'Номер родственника'},
                         {'t': 'x', 's': '//SPAN[text()="Номер друга"]', 'txt': 'Номер друга'},],
'ПлатежиКредитные' : [{'t': 'x', 's': '//SPAN[text()="Нет других кредитов"]', 'txt': 'Нет других кредитов'},
                      {'t': 'x', 's': '//SPAN[text()="Нет других кредитов"]', 'txt': 'Нет других кредитов'},
                      {'t': 'x', 's': '//SPAN[text()="Менее 10% дохода"]', 'txt': 'Менее 10% дохода'},
                      {'t': 'x', 's': '//SPAN[text()="От 10% до 25% дохода"]', 'txt': 'От 10% до 25% дохода'},
                      {'t': 'x', 's': '//SPAN[text()="От 25% до 50% дохода"]', 'txt': 'От 25% до 50% дохода'},
                      {'t': 'x', 's': '//SPAN[text()="Более 50% дохода"]', 'txt': 'Более 50% дохода'},],
'КредитнаяИстория' : [{'t': 'x', 's': '//SPAN[text()="Всегда плачу вовремя"]', 'txt': 'Всегда плачу вовремя'},
                      {'t': 'x', 's': '//SPAN[text()="Всегда плачу вовремя"]', 'txt': 'Всегда плачу вовремя'},
                      {'t': 'x', 's': '//SPAN[text()="Бывают просрочки"]', 'txt': 'Бывают просрочки'},
                      {'t': 'x', 's': '//SPAN[text()="Было много просрочек"]', 'txt': 'Было много просрочек'},
                      {'t': 'x', 's': '//SPAN[text()="Есть текущие просрочки"]', 'txt': 'Есть текущие просрочки'},
                      {'t': 'x', 's': '//SPAN[text()="Не было кредитов"]', 'txt': 'Не было кредитов'},
                      {'t': 'x', 's': '//SPAN[text()="Не знаю"]', 'txt': 'Не знаю'},], # Какая кредитная история
'Образование' : [{'t': 'x', 's': '//SPAN[text()="Начальное, среднее"]', 'txt': 'Не указано'},
                 {'t': 'x', 's': '//SPAN[text()="Начальное, среднее"]', 'txt': 'Начальное, среднее'},
                 {'t': 'x', 's': '//SPAN[text()="Неполное высшее"]', 'txt': 'Неполное высшее'},
                 {'t': 'x', 's': '//SPAN[text()="Высшее"]', 'txt': 'Высшее'},
                 {'t': 'x', 's': '//SPAN[text()="Второе высшее"]', 'txt': 'Второе высшее'},
                 {'t': 'x', 's': '//SPAN[text()="Ученая степень"]', 'txt': 'Ученая степень'},], # Образование
'СемейноеПоложение' : [{'t': 'x', 's': '//SPAN[text()="Холост/не замужем"]', 'txt': 'Не выбрано'},
                       {'t': 'x', 's': '//SPAN[text()="Холост/не замужем"]', 'txt': 'Холост/не замужем'},
                       {'t': 'x', 's': '//SPAN[text()="Разведен (а)"]', 'txt': 'Разведен (а)'},
                       {'t': 'x', 's': '//SPAN[text()="Гражданский брак"]', 'txt': 'Гражданский брак'},
                       {'t': 'x', 's': '//SPAN[text()="Женат/замужем"]', 'txt': 'Женат/замужем'},
                       {'t': 'x', 's': '//SPAN[text()="Вдовец, вдова"]', 'txt': 'Вдовец, вдова'},], # Семейное положение
'Автомобиль' : [{'t': 'x', 's': '//SPAN[text()="Нет"]', 'txt': 'Нет'},
                {'t': 'x', 's': '//SPAN[text()="Отечественный"]', 'txt': 'Отечественный'},
                {'t': 'x', 's': '//SPAN[text()="Иномарка"]', 'txt': 'Иномарка'},], # Автомобиль
'ЧастоЗагран' : [{'t': 'x', 's': '//SPAN[text()="Реже 1 раза в год"]', 'txt': 'Реже 1 раза в год'},
                {'t': 'x', 's': '//SPAN[text()="Реже 1 раза в год"]', 'txt': 'Реже 1 раза в год'},
                {'t': 'x', 's': '//SPAN[text()="1-2 раза в год"]', 'txt': '1-2 раза в год'},
                {'t': 'x', 's': '//SPAN[text()="3-5 раз в год"]', 'txt': '3-5 раз в год'},
                {'t': 'x', 's': '//SPAN[text()="Чаще 6 раз в год"]', 'txt': 'Чаще 6 раз в год'},],

'СкДетей' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[3]'    , 'SQL': "status_childs_code"}, # Количество детей
'ПросрочкиПоКредитам' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[8]'    , 'SQL': "status_credit_delay_code"}, # Просрочки по текущим кредитам
'ПрВодительскоеУд' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[9]'    , 'SQL': "driver_card_attachment_id"}, # Предоставит вод.удостоверение
'ПрЗагранпаспорт' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[10]'   , 'SQL': "international_passport_attachment_id"}, # Предоставит Загранпаспорт
'ПрПенсионноеУд' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[11]'   , 'SQL': "pensioner_card_attachment_id"}, # Предоставит Пенс.удостоверение
'ПрУдОфицера' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[12]'   , 'SQL': "identity_card_mvd_attachment_id"}, # Предоставит Удост.офицера МВД
'ПрВоенныйБилет' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[13]'   , 'SQL': "military_card_attachment_id"}, # Предоставит Военный билет
'ПрСвРегТС' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[14]'   , 'SQL': "auto_reg_attachment_id"}, # Cвидетельство регистрации ТС
'ПрОригПТС' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[15]'   , 'SQL': "auto_pts_attachment_id"}, # Оригинал ПТС
'ПрПолисКАСКО' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[16]'   , 'SQL': "auto_kasko_attachment_id"}, # Полис страхования КАСКО
'ПрПолисОСАГО' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[17]'   , 'SQL': "auto_osago_attachment_id"}, # Полис ОСАГО
'ПрСНИЛС' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[18]'   , 'SQL': "number_attachment_id"}, # Предоставит СНИЛС
'ПрИНН' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[19]'   , 'SQL': "inn_attachment_id"}, # Предоставит ИНН
'Пр2НДФЛ' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[20]'   , 'SQL': "has_2NDFL"}, # Предоставит 2 НДФЛ
'ПрСправкуОДоходах' : {'t': 'x', 's': '//[@class="tcs-plugin-select2"])[21]'   , 'SQL': "has_income_report"}, # Предоставит Справку о доходах
}

inputtity_first = [
                   "addresstype_registered_postal_code", "addresstype_registered_place",
                   "addresstype_registered_area", "addresstype_registered_city",
                   "addresstype_registered_street", "addresstype_registered_building",
                   "addresstype_registered_corpus", "addresstype_registered_flat", "addresstype_home_postal_code",
                   "addresstype_home_place", "addresstype_home_area", "addresstype_home_city",
                   "addresstype_home_street", "addresstype_home_building",
                   "addresstype_home_corpus", "addresstype_home_flat",
                   "addresstype_work_postal_code", "addresstype_work_place", "addresstype_work_area",
                   "addresstype_work_city", "addresstype_work_street", "addresstype_work_building",
                   "addresstype_work_corpus", "addresstype_work_flat"
                  ]


gluk_w_point = ["surname", "name", "patronymic", "passport_who_given", "place_of_birth",
                "addresstype_registered_place", "addresstype_registered_area", "addresstype_registered_city",
                "addresstype_registered_street",
                "addresstype_home_place", "addresstype_home_area", "addresstype_home_city","addresstype_home_street",
                "addresstype_work_place", "addresstype_work_area", "addresstype_work_city", "addresstype_work_street"
                ]


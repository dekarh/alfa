# -*- coding: utf-8 -*-

#
# Библиотека общих функций для selenium ver 1.02
#

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from configparser import ConfigParser

from mysql.connector import MySQLConnection, Error
import time
from datetime import datetime

import string
import sys
from random import uniform
from lib import unique

# DRIVER_PATH = 'drivers/chromedriver.exe'
#DRIVER_PATH = 'drivers/chromedriver'

def wr():
    time.sleep(uniform(0.5, 5))

def append_words(a, n_words):
    try:
        if a != None:
            for a1 in a.split(','):
                for a2 in a1.split(';'):
                    for a3 in a2.split(' '):
                        if a3 != '':
                            n_words.append(a3)
            unique(n_words)
            unique(n_words)
        return
    except TypeError:
        return

def wj(driver):  # Ждем, пока динамическая ява завершит все свои процессы
    #    WebDriverWait(driver, 50).until(lambda driver: driver.execute_script("return (typeof jQuery != 'undefined') ? jQuery.active == 0 : true"))

    WebDriverWait(driver, 50).until(lambda driver: driver.execute_script("return (typeof jQuery != 'undefined') ? jQuery.active == 0 : true"))

    """
    Еще варианты фреймворков/библиотек:
    "return jQuery.active == 0"
    "return Ajax.activeRequestCount == 0"
    "return dojo.io.XMLHTTPTransport.inFlight.length == 0"
    Ожидание пока все набранные буквы отработют явой:
    element = WebDriverWait(ff, 10).until(EC.presence_of_element_located((By.ID, "keywordSuggestion")))
    """
    return

def wa(driver): # Типа ловит анимацию. Здесь не ловит :(
    WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.ID, 'new - element') and
                                                   driver.find_elements(By.ID, 'spinner') == 0)
    return
"""
Прокрутка
driver.execute_script("return arguments[0].scrollIntoView();", elem) # Здесь не точно
driver.execute_script("window.scrollTo(0, 911)") # Здесь вообще не прокручивает

"""
def chk(d, t, s, f = '', a = '', SQL = '', txt = ''): # Проверка наличия элемента, не вызывающая исключения
    wj(d)
    try:
        if   t == 'i':
            d.find_element(By.ID, s)
        elif t == 'c':
            d.find_element(By.CLASS_NAME, s)
        elif t == 'x':
            d.find_element(By.XPATH, s)
    except NoSuchElementException:
        return False
    return True
"""
^^^
|||
Потому что EC.presence_of_element_located((By.XPATH, "xpath"))) возвращает объект, не нашел где там результат
try:
    assert EC.presence_of_element_located((By.XPATH, '//*[@id="Waldo"]')) is not True
except AssertionError, e:
    self.verificationErrors.append('presence_of_element_located returned True for Waldo')
"""

def p(d, t, f, s, a = '', data_id = '', e = '', SQL = '', txt = ''):
    wj(d)
    if data_id != '':
        data_id += '"]'
    if t == 'x':
        if   f == 'c':
            foo = WebDriverWait(d, 20).until(EC.element_to_be_clickable((By.XPATH, s + data_id + e)))
            wj(d)
            if a == '':
                return foo
            else:
                if a == 'text':
                    return foo.text
                else:
                    return foo.get_attribute(a)
        elif f == 'v':
            foo = WebDriverWait(d, 20).until(EC.visibility_of_element_located((By.XPATH, s + data_id + e)))
            wj(d)
            if a == '':
                return foo
            else:
                if a == 'text':
                    return foo.text
                else:
                    return foo.get_attribute(a)
        elif f == 'vs':
            foo = WebDriverWait(d, 20).until(EC.visibility_of_any_elements_located((By.XPATH, s + data_id + e)))
            wj(d)
            if a == '':
                return foo
            else:
                if a == 'text':
                    return [atr.text for atr in foo]
                else:
                    return [atr.get_attribute(a) for atr in foo]
        elif f == 'vv':
            if chk(d = d, t = t, s = s + data_id + e):
                wj(d)
                foo = WebDriverWait(d, 20).until(EC.presence_of_all_elements_located((By.XPATH, s + data_id + e)))
                wj(d)
                if a == '':
                    return foo
                else:
                    if a == 'text':
                        return [atr.text for atr in foo if atr.is_displayed()]
                    else:
                        return [atr.get_attribute(a) for atr in foo if atr.is_displayed()]
            else:
                if a == '':
                    return []
                else:
                    return ['']
        elif f == 'p':
            if chk(d = d, t = t, s = s + data_id + e):
                wj(d)
                foo = WebDriverWait(d, 20).until(EC.presence_of_element_located((By.XPATH, s + data_id + e)))
                wj(d)
                if a == '':
                    return foo
                else:
                    if a == 'text':
                        return foo.text
                    else:
                        return foo.get_attribute(a)
            else:
                if a == '':
                    return
                else:
                    return ''
        elif f == 'ps':
            if chk(d = d, t = t, s = s + data_id + e):
                wj(d)
                foo = WebDriverWait(d, 20).until(EC.presence_of_all_elements_located((By.XPATH, s + data_id + e)))
                wj(d)
                if a == '':
                    return foo
                else:
                    if a == 'text':
                        return [atr.text for atr in foo]
                    else:
                        return [atr.get_attribute(a) for atr in foo]
            else:
                if a == '':
                    return []
                else:
                    return ['']
        else:
            return



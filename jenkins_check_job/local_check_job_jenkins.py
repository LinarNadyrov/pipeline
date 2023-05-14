# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import json
import requests
from datetime import datetime, timedelta
import time

JENKINS_KEYCLOAK_USER = ''  # пример 'admin'
JENKINS_KEYCLOAK_PW = ''  # пример 'password'
CLIENT_ID_KEYCLOAK = ''  # пример 'ap-jenkins-test'
SECRET_KEYCLOAK = ''  # секрет кейклока
KEYCLOAK_REALM = ''  # Realm у прода users у теста USERS

ACCESS_TOKEN_FILE = 'TOKEN'
SCRIPT_TO_ACCESS_TOKEN = 'scripts/jenkins_check_job/keycloak.sh'
TOKEN_SRV_URL = '' # пример 'https://keycloak.com/auth'

JENKINS_URL = 'http'
JENKINS_DOMAIN = ' '  # пример 'my_domain'

# JENKINS API со списком всех JOB
JENKINS_ALL_LIST_BUILD = 'api/json?tree=jobs%5Bname%5D&pretty=true'
# JENKINS API со списком продолжительностью (duration) каждой JOB 
JENKINS_BUILD_DURATION = 'api/json?tree=builds[number,duration,timestamp,result]'

os.environ["AUTHORIZATION_CODE_LOGIN_PASSWORD"] = JENKINS_KEYCLOAK_PW

JENKINS_WORKING_LOADED_LIST = 'jenkins_up_list.txt'

time_stamp_script = time.time()
script_run_time = datetime.fromtimestamp(time_stamp_script)

# Время запуска скрипта
print("\n" + "=====")
print("Script run at:", script_run_time)
print("=====")

# Подключаемся к keycloak для получения ACCESS TOKEN
cmd_keycloak = 'bash ' + SCRIPT_TO_ACCESS_TOKEN + ' -a ' + TOKEN_SRV_URL + ' -r ' + KEYCLOAK_REALM + ' -c ' + CLIENT_ID_KEYCLOAK + ' -l ' + JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + ' -u ' + JENKINS_KEYCLOAK_USER + ' -s ' + SECRET_KEYCLOAK + " > " + ACCESS_TOKEN_FILE
shellcmd_keycloak = os.popen(cmd_keycloak)
shellcmd_keycloak.close()

## Функция, открываем файл и считываем его содержимое в список
def file_to_list(NAME_FILE, NAME_LIST):
    with open(NAME_FILE, 'r', encoding='utf-8') as filehandle:
        filecontents = filehandle.readlines()
        for line in filecontents:
            # удалим заключительный символ перехода строки
            current_place = line[:-1]
            # добавим элемент в конец списка
            NAME_LIST.append(current_place)

# Считываем запущенный список Jenkins в list
JENKINS_RUNNING_LIST = []
file_to_list(JENKINS_WORKING_LOADED_LIST,JENKINS_RUNNING_LIST)

# время создания TOKEN
time_stamp_token = (os.path.getatime('TOKEN'))
token_create_time = datetime.fromtimestamp(time_stamp_token)
print("\n" + "=====")
print('TOKEN CREATE AT:', token_create_time)
print("=====")

## Функция, открываем файл и считываем его содержимое в список
def token_to_list(NAME_FILE, NAME_LIST):
    with open(NAME_FILE, 'r', encoding='utf-8') as filehandle:
        for line in filehandle:
            NAME_LIST.append(line)

## Считываем TOKEN в list
TOKEN_LIST = []
token_to_list(ACCESS_TOKEN_FILE, TOKEN_LIST)
#print(TOKEN_LIST[0])

headers = {
    'Authorization': 'Bearer ' + TOKEN_LIST[0]}

# определяем, какая дата была N (180) дней (6 месяцев) назад от сегодняшней даты
N_DAYS_AGO = 180
today = datetime.now()
delta = timedelta(days=N_DAYS_AGO)
date = today - delta
six_months_ago = date.strftime('%d/%m/%Y')
#print('six_months_ago', six_months_ago)

# для сравнения двух дат используем time.struct_time, преобразовываем
six_months_ago = time.strptime(six_months_ago, "%d/%m/%Y")
#print('six_months_ago', six_months_ago)

# LIST для пустого Jenkins
JENKINS_EMPTY = []
# LIST для Jenkins у которых job'ы были запущены например 6 месяцев назад (временной интервал корректируется)
JENKINS_OLD_BUILDJOB = []

QUANTITY_JENKINS = 0
for data in JENKINS_RUNNING_LIST:
    JENKINS_NAME = data
    JENKINS_ADDR = JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + JENKINS_NAME + '/'
    #print('Мы тут', JENKINS_ADDR)
    QUANTITY_JENKINS += 1
    JENKINS_REQUEST = requests.get(JENKINS_ADDR, headers=headers)
    if str(JENKINS_REQUEST.status_code) == str(200):
        # забираем весь список существующих job в определенном Jenkins
        response = requests.post(JENKINS_ADDR + JENKINS_ALL_LIST_BUILD, headers=headers)
        json_var = json.loads(response.text)
        # определяем пустые Jenkins и вносим их в нужный нам список
        if json_var['jobs'] == []:
            JENKINS_EMPTY.append(JENKINS_ADDR)
        # иначе 
        else:
            # LIST для пустого Jenkins job
            JENKINS_JOB = []
            # находим список Jenkins job и вносим этот список в отдельный LIST 
            for ELEMENT in json_var['jobs']:
                JENKINS_JOB.append(ELEMENT.get('name'))
            # LIST для пустого timestamp job Jenkins
            JOB_TIMESTAMP = []
            # пробегаемся по всему списку Jenkins job и забираем их timestamp
            for builds in JENKINS_JOB:
                #print(builds)
                response = requests.post(JENKINS_ADDR + 'job/' + builds + '/' + JENKINS_BUILD_DURATION, headers=headers)
                json_var = json.loads(response.text)
                try:
                    # все timestamp Jenkins job собираем в один LIST 
                    for ELEMENT in json_var['builds']:
                        JOB_TIMESTAMP.append(ELEMENT.get('timestamp'))
                        # определяем дату самого последнего запуска Jenkins job
                        max_timestamp = max(JOB_TIMESTAMP)
                        max_timestamp = max_timestamp/1000
                        max_timestamp = datetime.fromtimestamp(max_timestamp).strftime('%d/%m/%Y')
                except: 
                    continue
            # для сравнения двух дат используем time.struct_time, преобразовываем
            max_timestamp = time.strptime(max_timestamp, "%d/%m/%Y")
            # проверяем условие
            if six_months_ago > max_timestamp or six_months_ago == max_timestamp:
                JENKINS_OLD_BUILDJOB.append(JENKINS_ADDR)
            else:
                continue

    elif str(JENKINS_REQUEST.status_code) == str(504):
        RETRIES = 1  ## Начало отчета
        RETRIES_CHECK = 6  ## Кол-во попыток 6-1=5 раз
        while RETRIES < RETRIES_CHECK:
            time.sleep(TIMEOUT)
            RETRIES += 1
            if str(JENKINS_REQUEST.status_code) == str(200):
                # забираем весь список существующих job в определенном Jenkins
                response = requests.post(JENKINS_ADDR + JENKINS_ALL_LIST_BUILD, headers=headers)
                json_var = json.loads(response.text)
                # определяем пустые Jenkins и вносим их в нужный нам список
                if json_var['jobs'] == []:
                    JENKINS_EMPTY.append(JENKINS_ADDR)
                # иначе 
                else:
                    # LIST для пустого Jenkins job
                    JENKINS_JOB = []
                    # находим список Jenkins job и вносим этот список в отдельный LIST 
                    for ELEMENT in json_var['jobs']:
                        JENKINS_JOB.append(ELEMENT.get('name'))
                    # LIST для пустого timestamp job Jenkins
                    JOB_TIMESTAMP = []
                    # пробегаемся по всему списку Jenkins job и забираем их timestamp
                    for builds in JENKINS_JOB:
                        #print(builds)
                        response = requests.post(JENKINS_ADDR + 'job/' + builds + '/' + JENKINS_BUILD_DURATION, headers=headers)
                        json_var = json.loads(response.text)
                        try:
                            # все timestamp Jenkins job собираем в один LIST 
                            for ELEMENT in json_var['builds']:
                                JOB_TIMESTAMP.append(ELEMENT.get('timestamp'))
                                # определяем дату самого последнего запуска Jenkins job
                                max_timestamp = max(JOB_TIMESTAMP)
                                max_timestamp = max_timestamp/1000
                                max_timestamp = datetime.fromtimestamp(max_timestamp).strftime('%d/%m/%Y')
                        except: 
                            continue
                    # для сравнения двух дат используем time.struct_time, преобразовываем
                    max_timestamp = time.strptime(max_timestamp, "%d/%m/%Y")
                    # проверяем условие
                    if six_months_ago > max_timestamp or six_months_ago == max_timestamp:
                        JENKINS_OLD_BUILDJOB.append(JENKINS_ADDR)
                    else:
                        continue

    elif str(JENKINS_REQUEST.status_code) == str(403):
        cmd_keycloak = 'bash ' + SCRIPT_TO_ACCESS_TOKEN + ' -a ' + TOKEN_SRV_URL + ' -r ' + KEYCLOAK_REALM + ' -c ' + CLIENT_ID_KEYCLOAK + ' -l ' + JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + ' -u ' + JENKINS_KEYCLOAK_USER + ' -s ' + SECRET_KEYCLOAK + " > " + ACCESS_TOKEN_FILE
        shellcmd_keycloak = os.popen(cmd_keycloak)
        shellcmd_keycloak.close()
        # время создания TOKEN
        time_stamp_token = (os.path.getctime('TOKEN'))
        token_create_time = datetime.fromtimestamp(time_stamp_token)
        time.sleep(1)
        TOKEN_LIST = []
        token_to_list(ACCESS_TOKEN_FILE, TOKEN_LIST)
        headers = {'Authorization': 'Bearer ' + TOKEN_LIST[0]}
        print("\n" + "=====")
        print('TOKEN UPDATE AT:', token_create_time)
        print("=====")
        JENKINS_REQUEST = requests.get(JENKINS_ADDR, headers=headers)
        if str(JENKINS_REQUEST.status_code) == str(200):
            # забираем весь список существующих job в определенном Jenkins
            response = requests.post(JENKINS_ADDR + JENKINS_ALL_LIST_BUILD, headers=headers)
            json_var = json.loads(response.text)
            # определяем пустые Jenkins и вносим их в нужный нам список
            if json_var['jobs'] == []:
                JENKINS_EMPTY.append(JENKINS_ADDR)
            # иначе 
            else:
                # LIST для пустого Jenkins job
                JENKINS_JOB = []
                # находим список Jenkins job и вносим этот список в отдельный LIST 
                for ELEMENT in json_var['jobs']:
                    JENKINS_JOB.append(ELEMENT.get('name'))
                # LIST для пустого timestamp job Jenkins
                JOB_TIMESTAMP = []
                # пробегаемся по всему списку Jenkins job и забираем их timestamp
                for builds in JENKINS_JOB:
                    #print(builds)
                    response = requests.post(JENKINS_ADDR + 'job/' + builds + '/' + JENKINS_BUILD_DURATION, headers=headers)
                    json_var = json.loads(response.text)
                    try:
                        # все timestamp Jenkins job собираем в один LIST 
                        for ELEMENT in json_var['builds']:
                            JOB_TIMESTAMP.append(ELEMENT.get('timestamp'))
                            # определяем дату самого последнего запуска Jenkins job
                            max_timestamp = max(JOB_TIMESTAMP)
                            max_timestamp = max_timestamp/1000
                            max_timestamp = datetime.fromtimestamp(max_timestamp).strftime('%d/%m/%Y')
                    except: 
                        continue
                # для сравнения двух дат используем time.struct_time, преобразовываем
                max_timestamp = time.strptime(max_timestamp, "%d/%m/%Y")
                # проверяем условие
                if six_months_ago > max_timestamp or six_months_ago == max_timestamp:
                    JENKINS_OLD_BUILDJOB.append(JENKINS_ADDR)
                else:
                    continue            

if len(JENKINS_EMPTY) > 1 or len(JENKINS_EMPTY) == 1:
    print('\n','List of empty Jenkins: ',sep='')
    print(JENKINS_EMPTY,'\n',sep='')

if len(JENKINS_OLD_BUILDJOB) > 1 or len(JENKINS_OLD_BUILDJOB) == 1:
    print('Jenkins running', N_DAYS_AGO,'days ago: ')
    print(JENKINS_OLD_BUILDJOB,'\n',sep='')

print('Total Jenkins:', len(JENKINS_RUNNING_LIST))
print('Processed Jenkins', QUANTITY_JENKINS)

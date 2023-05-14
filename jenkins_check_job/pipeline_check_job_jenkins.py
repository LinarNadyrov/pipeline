# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import json
import requests
from datetime import datetime, timedelta
import time
import argparse
from requests.auth import HTTPBasicAuth

parser = argparse.ArgumentParser(description='command line options')
parser.add_argument("-jenkins_url", "--jenkins_url", default=None, type=str, help="JENKINS_URL")
parser.add_argument("-jenkins_domain", "--jenkins_domain", default=None, type=str, help="JENKINS_DOMAIN")
parser.add_argument("-ku", "--keycloak_user", default=None, type=str, help="JENKINS_KEYCLOAK_USER")
parser.add_argument("-lp", "--keycloak_password", default=None, type=str, help="JENKINS_KEYCLOAK_PW")
parser.add_argument("-cik", "--client_id_keycloak", default=None, type=str, help="CLIENT_ID_KEYCLOAK")
parser.add_argument("-sk", "--secret_keycloak", default=None, type=str, help="SECRET_KEYCLOAK")
parser.add_argument("-tsu", "--token_srv_url", default=None, type=str, help="TOKEN_SRV_URL")
parser.add_argument("-kr", "--keycloak_realm", default=None, type=str, help="KEYCLOAK_REALM")
parser.add_argument("-marathon_login", "--marathon_login", default=None, type=str, help="MARATHON_LOGIN")
parser.add_argument("-marathon_pw", "--marathon_pw", default=None, type=str, help="MARATHON_PW")
parser.add_argument("-n_days_ago", "--n_days_ago", default=None, type=int, help="N_DAYS_AGO")
args = parser.parse_args()

JENKINS_URL = args.jenkins_url
JENKINS_DOMAIN = args.jenkins_domain
JENKINS_KEYCLOAK_USER = args.keycloak_user
JENKINS_KEYCLOAK_PW = args.keycloak_password
CLIENT_ID_KEYCLOAK = args.client_id_keycloak
SECRET_KEYCLOAK = args.secret_keycloak

ACCESS_TOKEN_FILE = 'TOKEN'
SCRIPT_TO_ACCESS_TOKEN = 'jenkins_check_job/keycloak.sh'
TOKEN_SRV_URL = args.token_srv_url
KEYCLOAK_REALM = args.keycloak_realm

MARATHON_SRV = ['srv-1', 'srv-2', 'srv-3']
MARATHON_LOGIN = args.marathon_login
MARATHON_PW = args.marathon_pw
URL_START = 'http://'
URL_MARATHON_API_LEADER = '/marathon/v2/leader'
URL_MARATHON_API_APPS = '/marathon/v2/apps'
headers = {'Content-type':'application/json'}

# JENKINS API со списком всех JOB
JENKINS_ALL_LIST_BUILD = 'api/json?tree=jobs%5Bname%5D&pretty=true'
# JENKINS API со списком продолжительностью (duration) каждой JOB 
JENKINS_BUILD_DURATION = 'api/json?tree=builds[number,duration,timestamp,result]'

os.environ["AUTHORIZATION_CODE_LOGIN_PASSWORD"] = JENKINS_KEYCLOAK_PW

PATH = '/tmp/'
JENKINS_WORKING_LOADED_LIST = 'jenkins_up_list.txt'

time_stamp_script = time.time()
script_run_time = datetime.fromtimestamp(time_stamp_script)

# Время запуска скрипта
print("\n" + "=====")
print("Script run at:", script_run_time)
print("=====")

# определяем лидера mesos-master
for URL_MARATHON_SRV in MARATHON_SRV:
    url = URL_START + URL_MARATHON_SRV + URL_MARATHON_API_LEADER
    res = requests.get(url, auth=HTTPBasicAuth(MARATHON_LOGIN, MARATHON_PW), headers=headers)
    # Данные в формате dict 
    JSON_DATA = res.json()
    # Преобразуем в srt
    for key in JSON_DATA.keys():
        if key == 'leader':
            MARATHON_LEADER = JSON_DATA.get(key)[:-5]

# подключаемся к лидеру mesos-master и забираем данные
cmd_marathon = "curl -X GET -H 'Content-Type: application/json' " + URL_START + MARATHON_LOGIN + ":" + MARATHON_PW + "@" + MARATHON_LEADER + URL_MARATHON_API_APPS + " | ./jq -r '.apps | .[] | select(.instances | contains(1)) | [.id] | @csv'" + " | cut -d '/' -f 2" + " | sort -n" + " | tr '/\n' '/\n' > " + PATH + JENKINS_WORKING_LOADED_LIST
shellcmd_marathon = os.popen(cmd_marathon) 
shellcmd_marathon.close()

# Подключаемся к keycloak для получения ACCESS TOKEN
cmd_keycloak = 'bash ' + SCRIPT_TO_ACCESS_TOKEN + ' -a ' + TOKEN_SRV_URL + ' -r ' + KEYCLOAK_REALM + ' -c ' + CLIENT_ID_KEYCLOAK + ' -l ' + JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + ' -u ' + JENKINS_KEYCLOAK_USER + ' -s ' + SECRET_KEYCLOAK + " > " + PATH + ACCESS_TOKEN_FILE
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
file_to_list(PATH + JENKINS_WORKING_LOADED_LIST,JENKINS_RUNNING_LIST)

# время создания TOKEN
time_stamp_token = (os.path.getatime(PATH + 'TOKEN'))
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
token_to_list(PATH + ACCESS_TOKEN_FILE, TOKEN_LIST)
#print(TOKEN_LIST[0])

headers = {
    'Authorization': 'Bearer ' + TOKEN_LIST[0]}

# определяем, какая дата была N (180) дней (6 месяцев) назад от сегодняшней даты
N_DAYS_AGO = args.n_days_ago
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

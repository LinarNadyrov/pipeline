# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import json
from datetime import timedelta
from datetime import datetime
import requests
import time

JENKINS_KEYCLOAK_USER = ''  # пример 'admin'
JENKINS_KEYCLOAK_PW = ''  # пример 'password'
CLIENT_ID_KEYCLOAK = ''  # пример 'jenkins-test'
SECRET_KEYCLOAK = ''  # секрет кейклока
KEYCLOAK_REALM = ''  # Realm 

ACCESS_TOKEN_FILE = 'TOKEN'
SCRIPT_TO_ACCESS_TOKEN = 'keycloak.sh'
TOKEN_SRV_URL = '' # пример 'https://idp-test.domain.net/auth'

JENKINS_URL = 'http'
JENKINS_DOMAIN = ''  # пример 'jenkins-domain'

# JENKINS API со списком всех JOB
JENKINS_ALL_LIST_BUILD = 'api/json?tree=jobs%5Bname%5D&pretty=true'
# JENKINS API со списком продолжительностью (duration) каждой JOB 
JENKINS_BUILD_DURATION = 'api/json?tree=builds[number,duration,timestamp,builtOn]'


os.environ["AUTHORIZATION_CODE_LOGIN_PASSWORD"] = JENKINS_KEYCLOAK_PW
TIMEOUT = 30

JENKINS_RUNNING_LIST = ['jenkins-name-1','jenkins-name-2'] # список jenkins

DURATION_FOR_CLUSTER_JENKINS = 0
JENKINS_CLUSTER_COUNT = len(JENKINS_RUNNING_LIST)

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
# print(TOKEN_LIST[0])

headers = {
    'Authorization': 'Bearer ' + TOKEN_LIST[0]}

for data in JENKINS_RUNNING_LIST:
    DURATION_FOR_JENKINS = 0
    JENKINS_NAME = data
    JENKINS_ADDR = JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + JENKINS_NAME + '/'
    JENKINS_REQUEST = requests.get(JENKINS_ADDR, headers=headers)
    if str(JENKINS_REQUEST.status_code) == str(200):
        # забираем весь список существующих job в определенном Jenkins
        response = requests.post(JENKINS_ADDR + JENKINS_ALL_LIST_BUILD, headers=headers)
        json_var = json.loads(response.text)
        JENKINS_JOB = []
        for ELEMENT in json_var['jobs']:
            JENKINS_JOB.append(ELEMENT.get('name'))

        # проходимся по списку job и определяем среднее время сборки
        print("=================================")
        print('Jenkins - ', JENKINS_ADDR, sep='')
        print('Quantity job - ', len(JENKINS_JOB))
        COUNT_JENKINS_JOB = len(JENKINS_JOB)

        for builds in JENKINS_JOB:
            response = requests.post(JENKINS_ADDR + 'job/' + builds + '/' + JENKINS_BUILD_DURATION, headers=headers)
            json_var = json.loads(response.text)
            AVG_COUNT = 0
            DURATION_ALL = 0
            try:
                for ELEMENT in json_var['builds']:
                    # print(ELEMENT)
                    DURATION_BUILD = ELEMENT.get('duration')
                    DURATION_ALL += DURATION_BUILD
                    AVG_COUNT += 1
                # print('Имя джобы - ', builds + ' кол-во строк -', AVG_COUNT)
                DURATION_ALL_TIME = DURATION_ALL / AVG_COUNT
                DURATION_FOR_JENKINS += DURATION_ALL_TIME
                # находим среднее время
                milliseconds = timedelta(milliseconds=DURATION_ALL_TIME)
                milliseconds = str(milliseconds)
                milliseconds = milliseconds.split(".")[0]
                # print('For job - ', builds, '\n', 'Average build time = ', milliseconds, '\n', sep='')
            except:
                # print('For job - ', builds, '\n', 'Average build time = 0:00:00', '\n', sep='')
                COUNT_JENKINS_JOB -= 1
                continue

    elif str(JENKINS_REQUEST.status_code) == str(504):
        RETRIES = 1  ## Начало отчета
        RETRIES_CHECK = 6  ## Кол-во попыток 6-1=5 раз
        while RETRIES < RETRIES_CHECK:
            # print('ТУТ')
            time.sleep(TIMEOUT)
            RETRIES += 1
            if str(JENKINS_REQUEST.status_code) == str(200):
                # забираем весь список существующих job в определенном Jenkins
                response = requests.post(JENKINS_ADDR + JENKINS_ALL_LIST_BUILD, headers=headers)
                json_var = json.loads(response.text)
                JENKINS_JOB = []
                for ELEMENT in json_var['jobs']:
                    JENKINS_JOB.append(ELEMENT.get('name'))

                # проходимся по списку job и определяем среднее время сборки
                print("=================================")
                print('Jenkins - ', JENKINS_ADDR, sep='')
                COUNT_JENKINS_JOB = len(JENKINS_JOB)
                for builds in JENKINS_JOB:
                    response = requests.post(JENKINS_ADDR + 'job/' + builds + '/' + JENKINS_BUILD_DURATION,headers=headers)
                    json_var = json.loads(response.text)
                    AVG_COUNT = 0
                    DURATION_ALL = 0
                    try:
                        for ELEMENT in json_var['builds']:
                            # print(ELEMENT)
                            DURATION_BUILD = ELEMENT.get('duration')
                            DURATION_ALL += DURATION_BUILD
                            AVG_COUNT += 1
                        # print('Имя джобы - ', builds + ' кол-во строк -', AVG_COUNT)
                        DURATION_ALL_TIME = DURATION_ALL / AVG_COUNT
                        DURATION_FOR_JENKINS += DURATION_ALL_TIME

                        # находим среднее время
                        milliseconds = timedelta(milliseconds=DURATION_ALL_TIME)
                        milliseconds = str(milliseconds)
                        milliseconds = milliseconds.split(".")[0]
                        # print('For job - ', builds, '\n', 'Average build time = ', milliseconds, '\n', sep='')
                    except:
                        # print('For job - ', builds, '\n', 'Average build time = 0:00:00', '\n', sep='')
                        COUNT_JENKINS_JOB -= 1
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
            JENKINS_JOB = []
            for ELEMENT in json_var['jobs']:
                JENKINS_JOB.append(ELEMENT.get('name'))

            # проходимся по списку job и определяем среднее время сборки
            print("=================================")
            print('Jenkins - ', JENKINS_ADDR, sep='')
            COUNT_JENKINS_JOB = len(JENKINS_JOB)
            for builds in JENKINS_JOB:
                response = requests.post(JENKINS_ADDR + 'job/' + builds + '/' + JENKINS_BUILD_DURATION, headers=headers)
                json_var = json.loads(response.text)
                AVG_COUNT = 0
                DURATION_ALL = 0
                try:
                    for ELEMENT in json_var['builds']:
                        # print(ELEMENT)
                        DURATION_BUILD = ELEMENT.get('duration')
                        DURATION_ALL += DURATION_BUILD
                        AVG_COUNT += 1
                    # print('Имя джобы - ', builds + ' кол-во строк -', AVG_COUNT)
                    DURATION_ALL_TIME = DURATION_ALL / AVG_COUNT
                    DURATION_FOR_JENKINS += DURATION_ALL_TIME

                    # находим среднее время
                    milliseconds = timedelta(milliseconds=DURATION_ALL_TIME)
                    milliseconds = str(milliseconds)
                    milliseconds = milliseconds.split(".")[0]
                    # print('For job - ', builds, '\n', 'Average build time = ', milliseconds, '\n', sep='')
                except:
                    # print('For job - ', builds, '\n', 'Average build time = 0:00:00', '\n', sep='')
                    COUNT_JENKINS_JOB -= 1
                    continue
    # находим среднее время для всех сборок в конкретном Jenkins
    try:
        DURATION_FOR_JENKINS_ALL = DURATION_FOR_JENKINS / COUNT_JENKINS_JOB
    except:
        DURATION_FOR_JENKINS_ALL = 0
        milliseconds_jenkins = timedelta(milliseconds=DURATION_FOR_JENKINS_ALL)
        milliseconds_jenkins = str(milliseconds_jenkins)
        milliseconds_jenkins = milliseconds_jenkins.split(".")[0]
        print('For Jenkins - ', data, '\n', 'Average build time = ', milliseconds_jenkins, '\n', sep='')
        print("=================================")
        DURATION_FOR_CLUSTER_JENKINS += DURATION_FOR_JENKINS_ALL
        JENKINS_CLUSTER_COUNT -= 1
        continue
    milliseconds_jenkins = timedelta(milliseconds=DURATION_FOR_JENKINS_ALL)
    milliseconds_jenkins = str(milliseconds_jenkins)
    milliseconds_jenkins = milliseconds_jenkins.split(".")[0]
    print('For Jenkins - ', data, '\n', 'Average build time = ', milliseconds_jenkins, '\n', sep='')
    print("=================================")
    DURATION_FOR_CLUSTER_JENKINS += DURATION_FOR_JENKINS_ALL

# Среднее время сборки для списка Jenkins
if JENKINS_CLUSTER_COUNT == 0:
    print('Jenkins list is empty!')
else:
    DURATION_FOR_CLUSTER_JENKINS = DURATION_FOR_CLUSTER_JENKINS / JENKINS_CLUSTER_COUNT
    milliseconds_jenkins_cluster = timedelta(milliseconds=DURATION_FOR_CLUSTER_JENKINS)
    milliseconds_jenkins_cluster = str(milliseconds_jenkins_cluster)
    milliseconds_jenkins_cluster = milliseconds_jenkins_cluster.split(".")[0]
    print('For Jenkins in list - ', JENKINS_RUNNING_LIST, '\n','Jenkins count is - ', len(JENKINS_RUNNING_LIST),'\n''Average build time = ', milliseconds_jenkins_cluster, sep='')
    print("=================================")
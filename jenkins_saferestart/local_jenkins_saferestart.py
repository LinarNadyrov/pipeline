# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import requests
import time
from datetime import datetime

JENKINS_KEYCLOAK_USER = ""  # пример 'admin'
JENKINS_KEYCLOAK_PW = ""  # пример 'password'
CLIENT_ID_KEYCLOAK = ''  # пример 'ap-jenkins-test'
SECRET_KEYCLOAK = ''  # секрет кейклока
KEYCLOAK_REALM = ''  #Realm у прода users у теста USERS

ACCESS_TOKEN_FILE = 'TOKEN'
SCRIPT_TO_ACCESS_TOKEN = 'scripts/jenkins_saferestart/keycloak.sh'
TOKEN_SRV_URL = '' # пример 'https://idp-test.alfaintra.net/auth'

JENKINS_URL = 'http'
JENKINS_DOMAIN = ""  # пример 'dojenkins'
JENKINS_SAFE_RESTART_API = 'safeRestart'


os.environ["AUTHORIZATION_CODE_LOGIN_PASSWORD"] = JENKINS_KEYCLOAK_PW
TIMEOUT = 30

JENKINS_RUNNING_LIST = ['jenkins_name_1','jenkins_name_2'] # список jenkins

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
token_to_list(ACCESS_TOKEN_FILE,TOKEN_LIST)

headers = {
    'Authorization': 'Bearer ' + TOKEN_LIST[0]}

for data in JENKINS_RUNNING_LIST:
    JENKINS_NAME = data
    JENKINS_ADDR = JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + JENKINS_NAME + '/'
    JENKINS_REQUEST = requests.get(JENKINS_ADDR, headers=headers)
    if str(JENKINS_REQUEST.status_code) == str(200):
        response = requests.post(JENKINS_ADDR + JENKINS_SAFE_RESTART_API, headers=headers)
    elif str(JENKINS_REQUEST.status_code) == str(504):
        RETRIES = 1 ## Начало отчета
        RETRIES_CHECK = 6 ## Кол-во попыток 6-1=5 раз
        while RETRIES < RETRIES_CHECK:
            print('ТУТ')
            time.sleep(TIMEOUT)
            RETRIES += 1
            if str(JENKINS_REQUEST.status_code) == str(200):
                response = requests.post(JENKINS_ADDR + JENKINS_SAFE_RESTART_API, headers=headers)
                RETRIES = RETRIES_CHECK
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
            response = requests.post(JENKINS_ADDR + JENKINS_SAFE_RESTART_API, headers=headers)
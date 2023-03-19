# -*- coding: utf-8 -*-
#!/usr/bin/python

import requests
from requests.auth import HTTPBasicAuth
import json
import os
import numpy as np
import argparse
import time
from datetime import datetime

parser = argparse.ArgumentParser(description='command line options')
parser.add_argument("-jenkins_url", "--jenkins_url", default=None, type=str, help="JENKINS_URL")
parser.add_argument("-jenkins_domain", "--jenkins_domain", default=None, type=str, help="JENKINS_DOMAIN")
parser.add_argument("-ku", "--keycloak_user", default=None, type=str, help="JENKINS_KEYCLOAK_USER")
parser.add_argument("-lp", "--keycloak_password", default=None, type=str, help="JENKINS_KEYCLOAK_PW")
parser.add_argument("-cik", "--client_id_keycloak", default=None, type=str, help="CLIENT_ID_KEYCLOAK")
parser.add_argument("-sk", "--secret_keycloak", default=None, type=str, help="SECRET_KEYCLOAK")
parser.add_argument("-tsu", "--token_srv_url", default=None, type=str, help="TOKEN_SRV_URL")
parser.add_argument("-kr", "--keycloak_realm", default=None, type=str, help="KEYCLOAK_REALM")
parser.add_argument("-jsr", "--jenkins_running_list", default=None, type=str, help="JENKINS_SAFE_RESTART_LIST")
args = parser.parse_args()

JENKINS_URL = args.jenkins_url
JENKINS_DOMAIN = args.jenkins_domain
JENKINS_KEYCLOAK_USER = args.keycloak_user
JENKINS_KEYCLOAK_PW = args.keycloak_password
CLIENT_ID_KEYCLOAK = args.client_id_keycloak
SECRET_KEYCLOAK = args.secret_keycloak

ACCESS_TOKEN_FILE = 'TOKEN'
SCRIPT_TO_ACCESS_TOKEN = 'jenkins_saferestart/keycloak.sh'
TOKEN_SRV_URL = args.token_srv_url
KEYCLOAK_REALM = args.keycloak_realm
JENKINS_SAFE_RESTART_API = 'safeRestart'

os.environ["AUTHORIZATION_CODE_LOGIN_PASSWORD"] = JENKINS_KEYCLOAK_PW
TIMEOUT = 30

JENKINS_RUNNING_LIST = args.jenkins_running_list.replace(',', ' ')
JENKINS_RUNNING_LIST = JENKINS_RUNNING_LIST.split()

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
if script_run_time < token_create_time and TOKEN_LIST[0] != [] and TOKEN_LIST[0] != str('null') and TOKEN_LIST[0] != str(404) and TOKEN_LIST[0] != str(403) and TOKEN_LIST[0] != str(503):
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
                #print('ТУТ')
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
else:
    print('Please check script_run_time or null or errors 404 503 and etc')
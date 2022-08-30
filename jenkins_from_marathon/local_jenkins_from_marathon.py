# -*- coding: utf-8 -*-
#!/usr/bin/python

import requests
from requests.auth import HTTPBasicAuth
import json
import os
import numpy as np
import jenkins
import argparse
import time

JENKINS_URL = 'http'
JENKINS_DOMAIN = 'jenkins-domain'
JENKINS_NAME = 'jenkins-name'

JENKINS_LDAP_USER = ''                 # пример 'admin'
JENKINS_LDAP_PW = ''                   # пример 'password'

MARATHON_SRV = ['srv-1', 'srv-2', 'srv-3']
MARATHON_LOGIN = ''    # пример 'admin'
MARATHON_PW = ''       # пример 'password'
URL_START = 'http://'
URL_MARATHON_API_LEADER = '/marathon/v2/leader'
URL_MARATHON_API_APPS = '/marathon/v2/apps'
headers = {'Content-type':'application/json'}
JENKINS_LOADED_LIST = 'jenkins_up_list.txt'
JENKINS_PROFILE_CURRENT = 'jenkins_profile.txt'

# разделяем общий список на n=8 ровных частей
NUMBER_THREADS = 8
# тайм-аут (секунды)
NUMBER_TIME_OUT = 120

# !!! список Jenkins которые не перекатываем !!!
JENKINS_DO_NOT_ROLL = ['jenkins-name1','jenkins-name2','jenkins-name3']

# локальная директория jenkins_profile
JENKINS_PROFILE_PATH = '/Users/linarnadyrov/Document/github/pipeline'

cmd_jenkins_profile = "ls -l " + JENKINS_PROFILE_PATH + " | grep 'yml'| awk '{ print $9}' | sed 's/\..*//' > " + JENKINS_PROFILE_CURRENT
shellcmd_jenkins_profile = os.popen(cmd_jenkins_profile) 
shellcmd_jenkins_profile.close()

# определяем пустой список для jenkins_profile
JENKINS_PROFILE_LIST = []
# открываем файл и считываем его содержимое в список
with open(JENKINS_PROFILE_CURRENT, 'r', encoding='utf-8') as filehandle:  
    filecontents = filehandle.readlines()
    for line in filecontents:
        # удалим заключительный символ перехода строки
        current_place = line[:-1]
        # добавим элемент в конец списка
        JENKINS_PROFILE_LIST.append(current_place)

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
#print('MARATHON_LEADER:','\n',MARATHON_LEADER)

# подключаемся к лидеру mesos-master и забираем данные
cmd_marathon = "curl -X GET -H 'Content-Type: application/json' " + URL_START + MARATHON_LOGIN + ":" + MARATHON_PW + "@" + MARATHON_LEADER + URL_MARATHON_API_APPS + " | jq -r '.apps | .[] | select(.instances | contains(1)) | [.id] | @csv'" + " | cut -d '/' -f 2" + " | sort -n" + " | tr '/\n' '/\n' > " + JENKINS_LOADED_LIST
shellcmd_marathon = os.popen(cmd_marathon) 
shellcmd_marathon.close()

# определяем пустой список для jenkins from marathon
JENKINS_ALL_LIST = []
# открываем файл и считываем его содержимое в список
with open(JENKINS_LOADED_LIST, 'r', encoding='utf-8') as filehandle:  
    filecontents = filehandle.readlines()
    for line in filecontents:
        # удалим заключительный символ перехода строки
        current_place = line[:-1]
        # добавим элемент в конец списка
        JENKINS_ALL_LIST.append(current_place)
print("\n", "Total Up Jenkins  = ",len(JENKINS_ALL_LIST))

# сравниваем два списка (JENKINS_ALL_LIST и JENKINS_PROFILE_LIST) и находим jenkins у которого нет profile
JENKINS_NO_PROFILE = [element for element in JENKINS_PROFILE_LIST + JENKINS_ALL_LIST if element not in JENKINS_PROFILE_LIST]
print("\n", "Jenkins у которых нет profile = ", JENKINS_NO_PROFILE, "\n")

# в список JENKINS_DO_NOT_ROLL добавляем список JENKINS_NO_PROFILE, этот общий список будет удален из JENKINS_ALL_LIST
for i in JENKINS_NO_PROFILE:
    JENKINS_DO_NOT_ROLL.append(i)
print("\n", "Jenkins удаленные из общего списка перекатки = ", JENKINS_DO_NOT_ROLL, "\n")

# из общего списка (JENKINS_ALL_LIST) загруженных jenkins удаляем указанные jenkins (JENKINS_DO_NOT_ROLL)
JENKINS_ALL_LIST = [ele for ele in JENKINS_ALL_LIST if ele not in JENKINS_DO_NOT_ROLL]

# разделяем общий список (JENKINS_ALL_LIST) на NUMBER_THREADS частей (не очень нравится, так как нужно ставить модуль - самый легкий способ)
print("\n", len(JENKINS_ALL_LIST), "Jenkins для перекатки, разделенный на", NUMBER_THREADS, "частей:", "\n")
splits = np.array_split(JENKINS_ALL_LIST, NUMBER_THREADS)

# подключаемся к Jenkins и отправляем на перекатку нужное количество
JENKINS_ADDR = JENKINS_URL + '://' + JENKINS_DOMAIN + '/' + JENKINS_NAME + '/'
server = jenkins.Jenkins(JENKINS_ADDR, username=JENKINS_LDAP_USER, password=JENKINS_LDAP_PW)
# user = server.get_whoami()
# version = server.get_version()
# print(version)

jenkins_job = 'jenkins-name-job'

for element in range(NUMBER_THREADS):
    lol_string = ','.join(map(str, splits[element]))
    print(lol_string)
    server.build_job(jenkins_job, {'name_jenkinsList': lol_string})
    time.sleep(NUMBER_TIME_OUT)

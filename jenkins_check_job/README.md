#### Скрипт:
```
1) подключается к keycloak для получения ACCESS TOKEN.
2) с полученным ACCESS TOKEN подключаемся к Jenkins.
3) вычисляет пустые Jenkins и Jenkins запущенные N времени назад. По умолчанию N = 180 дней (6 месяцев назад).
```

#### Тестирование проводилось на macOS Big Sur version 11.6 в python 3.7, создавал виртуальную среду во избежание конфликтов с пакетами системы
```
Пример активации виртуальной среды: 

python3.7 -m venv jenkins_check_job
source jenkins_check_job/bin/activate
```
#### После активации виртуальной среды, в терминале должен изменится ввод команд. Например:
```
(jenkins_check_job):~$ pip list
```
#### Установка нужного модуля
```
pip install requests
pip install python-dateutil
```
#### Запуск скрипта
```
python3 local_check_job_jenkins.py
```

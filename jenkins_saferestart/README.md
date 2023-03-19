#### Скрипт:
```
1) подключается к keycloak для получения ACCESS TOKEN
2) с полученным ACCESS TOKEN идет к нужному Jenkins и выполняется safeRestart
```

#### Тестирование проводилось на macOS Big Sur version 11.6 в python 3.7, создавал виртуальную среду во избежание конфликтов с пакетами системы
```
Пример активации виртуальной среды: 

python3.7 -m venv jenkins_saferestart
source jenkins_saferestart/bin/activate
```
#### После активации виртуальной среды, в терминале должен изменится ввод команд. Например:
```
(jenkins_from_marathon):~$ pip list
```
#### Установка нужного модуля
```
pip install requests

```
#### Пример запуска скрипта
```
python3 ../Users/linarnadyrov/Document/github/pipeline/jenkins_saferestart/jenkins_saferestart.py
```

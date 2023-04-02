#### Скрипт:
```
1) подключается к keycloak для получения ACCESS TOKEN.
2) подсчитыавает среднее время сборки на определенном Jenkins.
3) подсчитыавает среднее время сборки на всего кластера Jenkins.
```

#### Тестирование проводилось на macOS Big Sur version 11.6 в python 3.7, создавал виртуальную среду во избежание конфликтов с пакетами системы
```
Пример активации виртуальной среды: 

python3.7 -m venv jenkins_build_duration
source jenkins_build_duration/bin/activate
```
#### После активации виртуальной среды, в терминале должен изменится ввод команд. Например:
```
(jenkins_build_duration):~$ pip list
```
#### Установка нужного модуля
```
pip install requests

```
#### Пример запуска скрипта
```
python3 ../Users/linarnadyrov/Document/github/pipeline/jenkins_build_duration/local_jenkins_build_duration.py
```

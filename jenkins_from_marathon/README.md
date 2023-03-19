### Скрипт
### 1) определяет Mesos-master и подключается к нему
### 2) получает список запущенных экземпляров Jenkins из Marathon
### 3) полученный список делит на N (задается руками) частей

### Тестирование проводилось на macOS Big Sur version 11.6 в python 3.7, создавал виртуальную среду во избежание конфликтов с пакетами системы
```
Пример активации виртуальной среды: 

python3.7 -m venv jenkins_from_marathon
source jenkins_from_marathon/bin/activate
```
### После активации виртуальной среды, в терминале должен изменится ввод команд. Например:
```
(jenkins_from_marathon):~$ pip list
```
### Установка нужного модуля
```
pip install python-jenkins
pip install numpy 
pip install requests
```
### Запуск скрипта
```
python3 ../Users/linarnadyrov/Document/github/pipeline/local_jenkins_from_marathon.py
```

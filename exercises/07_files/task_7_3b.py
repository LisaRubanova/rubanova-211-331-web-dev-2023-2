# -*- coding: utf-8 -*-
"""
Задание 7.3b

Сделать копию скрипта задания 7.3a.

Переделать скрипт:
- Запросить у пользователя ввод номера VLAN.
- Выводить информацию только по указанному VLAN.

Пример работы скрипта:

Enter VLAN number: 10
10       0a1b.1c80.7000      Gi0/4
10       01ab.c5d0.70d0      Gi0/8

Ограничение: Все задания надо выполнять используя только пройденные темы.
words
"""
result = []
vlan_input = input("Номер VLAN: ")
with open('CAM_table.txt') as f:
    for line in f:
        text = line.split()
        temp = '{:15} {:15} {:15}'
        if text and text[0].isdigit():
            vlan, mac, _, ports = text
            result.append([int(vlan), mac, ports])
#print(result)
for vlan, mac, intf in sorted(result):
    if int(vlan_input) == vlan:
        print(f"{vlan:<9}{mac:20}{intf}")
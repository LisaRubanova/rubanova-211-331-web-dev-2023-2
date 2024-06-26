# -*- coding: utf-8 -*-
"""
Задание 5.2

Запросить у пользователя ввод IP-сети в формате: 10.1.1.0/24

Затем вывести информацию о сети и маске в таком формате:

Network:
10        1         1         0
00001010  00000001  00000001  00000000

Mask:
/24
255       255       255       0
11111111  11111111  11111111  00000000

Проверить работу скрипта на разных комбинациях сеть/маска.

Вывод сети и маски должен быть упорядочен также, как в примере:
- столбцами
- ширина столбца 10 символов (в двоичном формате
  надо добавить два пробела между столбцами
  для разделения октетов между собой)

Подсказка: Получить маску в двоичном формате можно так:
In [1]: "1" * 28 + "0" * 4
Out[1]: '11111111111111111111111111110000'


Ограничение: Все задания надо выполнять используя только пройденные темы.
"""
net = input('Введите ip адрес в формате a.a.a.a/b: ') 
ip, mask = net.split("/")
list_ip = ip.split(".")
mask = int(mask)

oct1, oct2, oct3, oct4 = [
    int(list_ip[0]),
    int(list_ip[1]),
    int(list_ip[2]),
    int(list_ip[3]),
]

mask_bin = "1" * mask + "0" * (32 - mask)
m_part1, m_part2, m_part3, m_part4 = [
  # 0-8  8-16  16-24  24-32
    int(mask_bin[0:8], 2),
    int(mask_bin[8:16], 2),
    int(mask_bin[16:24], 2),
    int(mask_bin[24:32], 2),
]
ip_out = """
Network:
{0:<8}  {1:<8}  {2:<8}  {3:<8}
{0:08b}  {1:08b}  {2:08b}  {3:08b}"""

mask_out = """
Mask:
/{0}
{1:<8}  {2:<8}  {3:<8}  {4:<8}
{1:08b}  {2:08b}  {3:08b}  {4:08b}
"""

print(ip_out.format(oct1, oct2, oct3, oct4))
print(mask_out.format(mask, m_part1, m_part2, m_part3, m_part4))
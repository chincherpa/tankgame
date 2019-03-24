import sys
from time import sleep
import random
from terminaltables import SingleTable
from tank import Tank


def spinning_cursor(duration, value):
    for i in range(duration):
        for c in '|/-\\':
            print(value, c)
            sleep(0.1)



# table_data = [
#     ['abc', '192.168.0.100', '192.168.0.101'],
#     ['def', '192.168.0.102, 192.168.0.103'],
#     ['ghi', '192.168.0.105'],
# ]
# table_instance = SingleTable(table_data)
# table_instance.inner_heading_row_border = False
# print(table_instance.table)

tanks = {
    '1': Tank('Alice the Menace', 80, 10, 12),
    '2': Tank('Bill the Grill', 70, 11, 13),
}

alive_tanks = len(tanks)

while alive_tanks:
    # name, armor, ammo, power
    table_data = [['Name', 'Armor', 'Ammo', 'Power', 'Kürzel']]
    counter = 1
    for tank in tanks.keys():
        table_data.append([tanks[tank].name, tanks[tank].armor, tanks[tank].ammo, tanks[tank].power, counter])
        counter += 1

    table_instance = SingleTable(table_data)
    for i in range(1, 5):
        table_instance.justify_columns[i] = 'center'
    print(table_instance.table)

    aktiv = input('Wer feuert?')
    try:
        aktiv_tank = tanks[aktiv]
    except KeyError:
        print('Keinen solchen Panzer gefunden!')
        continue
    passiv = input(f'{aktiv_tank.name} feuert auf?')

    try:
        passiv_tank = tanks[passiv]
    except KeyError:
        print('Keinen solchen Panzer gefunden!')
        continue

    if aktiv == passiv:
        print(f'{aktiv_tank.name} kann nicht auf sich selbst schiessen!')
        continue

    if not aktiv_tank.alive:
        print(f'{aktiv_tank.name} ist bereits zerstört!')
        continue
    elif not passiv_tank.alive:
        print(f'{passiv_tank.name} ist bereits zerstört!')
        continue

    spinning_cursor(3, 'Calculating...')
    treffer = random.randint(1, 101)

    aktiv_tank.fire_at(passiv_tank, treffer)




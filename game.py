from tank import Tank
import random
from terminaltables import SingleTable

# table_data = [
#     ['abc', '192.168.0.100', '192.168.0.101'],
#     ['def', '192.168.0.102, 192.168.0.103'],
#     ['ghi', '192.168.0.105'],
# ]
# table_instance = SingleTable(table_data)
# table_instance.inner_heading_row_border = False
# print(table_instance.table)

tanks = {
    1: Tank('Alice the Menace', 100, 10, 12),
    2: Tank('Bill the Grill', 90, 11, 13),
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
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)

    aktiv = input('Wer feuert?')
    try:
        aktiv_tank = tanks[aktiv]
    except KeyError:
        print('Keinen solchen Panzer gefunden!')
        continue
    passiv = input(f'{aktiv_tank.name} feuert auf?')

    try:
        aktiv_tank = tanks[aktiv]
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

    treffer = random.randint(1, 101)

    aktiv_tank.fire_at(passiv_tank, treffer)




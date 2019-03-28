#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from time import sleep
import random

from terminaltables import SingleTable
from colorclass import Color, Windows

from tank import *  # Tank

Windows.enable(auto_colors=True, reset_atexit=True)  # Does nothing if not on Windows.

# TODO: Shop - Done
# TODO: dead tanks can't go to the shop
# TODO: vs. Computer
# TODO: 2 Players
# TODO: player chooses name
# TODO: choose from predefined tanks
# TODO: dodging
# TODO: network

'''
?????
 - Cap malfunction ?
'''


def get_alive_tanks():
    c = 0
    for tank in tanks.keys():
        c += tanks[tank].alive
    return c


def spinning_cursor(duration, value=None):
    for _ in range(duration):
        for cursor in '|/-\\':
            sleep(0.1)
            sys.stdout.write(f'\r{cursor} {value}')
            sys.stdout.flush()
    print('\n')


items = {   # 'Item', 'effect', 'value', 'Price', parameter
    '0': ('Cancel', 'Close shop'),
    '1': ('Armor+10', 'Increase armor',    10, 3, 'armor'),
    '2': ('Armor+20', 'Increase armor',    20, 5, 'armor'),
    '3': ('Ammo+2', 'Ammo',                 2, 3, 'ammo'),
    '4': ('Repair', 'Decrease malfunction', 1, 2, 'malfunction'),
    '5': ('item5', 'effect5',               1, 100, 'param5'),
}


def show_shop(buyer):
    print('\n')
    print(str(buyer), '\n')
    try:
        shop_table = [['#', 'Item', 'Effect', ' Value', 'Price'],                               # Header
                      ['1', items['1'][0], items['1'][1], items['1'][2], items['1'][3]],        # Armor+10
                      ['2', items['2'][0], items['2'][1], items['2'][2], items['2'][3]],        # Armor+20
                      ['3', items['3'][0], items['3'][1], items['3'][2], items['3'][3]],        # Ammo+2
                      ['4', items['4'][0], items['4'][1], items['4'][2], items['4'][3]],        # item4
                      ['', '', '', ''],                                                         # item5
                      ['0', items['0'][0], items['0'][1]]]                                      # Cancel

        shop_table_instance = SingleTable(shop_table, 'Shop')
        # for i in range(2, 60):
        #     shop_table_instance.justify_columns[i] = 'center'
        print(shop_table_instance.table)
    except KeyError as e:
        print('------------------------------------------------')
        print(f'Error: {e.name}')
        print('------------------------------------------------')

    item = input('What do you want to buy?  ')

    if item in '01234':
        if item == '0':
            return False
        elif items[item][3] <= buyer.credits:
            print(f'{buyer.name} buys {items[item][0]} for {items[item][3]} credits\n')
            sleep(2)
            # '1': ('Armor+10', 'Increase armor', 10, 3),
            # '2': ('Armor+20', 'Increase armor', 20, 5),
            # '3': ('Shell+2', '2 shells', 2, 3),
            if item == '1':                    # 10 armor
                buyer.armor += items[item][2]
                print(f'{buyer.name} increased his armor by 10.\n')
            elif item == '2':                  # 20 armor
                buyer.armor += items[item][2]
                print(f'{buyer.name} increased his armor by 20.\n')
            elif item == '3':                  # 2 shells
                buyer.ammo += items[item][2]
                print(f'{buyer.name} gets 2 shells.\n')
            elif item == '4':                  # 2 shells
                buyer.malfunction -= items[item][2]
                print(f'{buyer.name} decreased his propability to malfunc by 1.\n')

            buyer.credits -= items[item][3]
            sleep(3)
            return True
        else:
            print(f'Not enough credits to buy {items[item][0]}!')
            print(f'{items[item][0]} costs {items[item][3]} credits.')
            print(f'You have {buyer.credits} credits.\n')
            return False
    else:
        print('Item does ot exist!')
        return False


##################
##### Instructions

skip = not True
if not skip:
    print('\n\nInstructions:\n\n'
          'Every tank has these attributes:\n'
          '  - name           : Name of the tank/player\n'
          '  - armor          : amount of armor, decreased (-damage) when hit (min = 0)\n'
          '  - ammo           : amount of shells, -1 per shot\n'
          '  - power          : damage per shell\n'
          '  - alive          : is tank alive?, starts with TRUE\n'
          '  - dmg_mitigation : Mitigation of incoming damage, -1 per hit (min = 0)\n'
          '  - credits        : amount of credits, starts with ' + str(SETTINGS['credits']) + '\n'
          '\n'
          '  --- SETTINGS ---\n'
          '  - miss           : tanks can miss by ' + str(SETTINGS['probability_to_miss']) + '%\n'
          '  - malfunction    : tanks can have malfunction by ' + str(
        SETTINGS['probability_of_malfunction']) + '%, increased by 1 when hit\n\n'
          )

    input('Press ENTER to start...')
else:
    print('\n\nInstructions skipped\n')

mode = False
pvp = False
pvc = False
while not mode:
    mode = input('\nPlayer vs. [P]layer or [C]omputer?')
    if mode.lower() == 'p':
        pvp = True
        tanks = {     # NAME    armor|ammo|power|dmg_mitigation %
            '1': Tank('Björn',  120,  10,  12,   15),
            '2': Tank('Lutz',   90,   13,  12,   18),
            '3': Tank('Martin', 115,  10,  13,   16),
        }
    elif mode.lower() == 'c':
        pvc = True
        tanks = {     # NAME      armor|ammo|power|dmg_mitigation %
            '1': Tank('Player99', 120,  10,  12,   15),
            'c': Tank('Computer',  90,  13,  12,   18),
        }
    else:
        mode = False


for tank in tanks.keys():
    print(str(tanks[tank]))
    print('\n')

alive_tanks = get_alive_tanks()

ltanks = []
for tank in tanks.keys():
    ltanks.append(tanks[tank].name)

while alive_tanks:

    os.system('cls' if os.name == 'nt' else 'clear')

    c = 0
    for tank in tanks.keys():
        c += tanks[tank].alive

    #############################
    ##### Create table with tanks
    tank_table = [['#', 'Name', 'Armor', 'Ammo', 'Power', 'Dmg red.', 'Miss', 'Malf.', 'Credits']]
    counter = 1
    for tank in tanks.keys():
        if tanks[tank].alive:
            name = Color('{autogreen}{}{/autogreen}').format(tanks[tank].name)
        else:
            name = Color('{autored}{}{/autored}').format(tanks[tank].name)

        armor = tanks[tank].armor
        if tanks[tank].armor < 51:
            armor = Color('{autoyellow}{}{/autoyellow}').format(tanks[tank].armor)
        if tanks[tank].armor < 26:
            armor = Color('{autored}{}{/autored}').format(tanks[tank].armor)

        tank_table.append(
            [counter, name, armor, tanks[tank].ammo, tanks[tank].power, tanks[tank].dmg_mitigation, tanks[tank].miss,
             tanks[tank].malfunction, tanks[tank].credits])
        counter += 1
    table_instance = SingleTable(tank_table, 'Tanks')
    for i in range(2, 60):
        table_instance.justify_columns[i] = 'center'
    print(table_instance.table)

    if pvp:
        #####################
        ##### get active tank
        active = input('Active tank?  ')
        
        # input = 1s     1 to shop
        if active[0] in tanks.keys() and len(active) == 2:
            if active[1].lower() == 's':
                active_tank = tanks[active[0]]
                show_shop(active_tank)
                sleep(3)
                continue

        # input = 1e3    1 shoots 3
        elif active[0] in tanks.keys() and len(active) == 3:
            if active[0] != active[2]:
                if active[1].lower() == 'e':
                    if active[2] in tanks.keys():
                        active_tank = tanks[active[0]]
                        action = active[1].lower()
                        passiv_tank = tanks[active[2]]
            else:
                print('Tanks cannot shoots at themselves') 

        else:
            # If (part of) Name is typed in, instead of number
            for t in ltanks:
                if active.lower() in t.lower():
                    active = str(ltanks.index(t) + 1)
                    break
            # check if tank exists
            try:
                active_tank = tanks[active]
            except KeyError:
                # Start again, if not
                print('Tank does not exist!')
                continue
        
            print(f'\n-> {active_tank.name}\n')
        
            action = input('Shoot an [E]nemy or go to [S]hop?  ')
        
            if action.lower() == 's':
                show_shop(active_tank)
                sleep(3)
                continue
                # result = show_shop(aktiv_tank)
                # if result is None:
                #     continue
                # else:                         What else? -> continue
                #     continue
            elif action.lower() == 'e':
                ######################
                ##### get passive tank
                passiv = input('Target?  ')
                # If (part of) Name is typed in, instead of number
                for t in ltanks:
                    if passiv.lower() in t.lower():
                        # print(f'Hier: {t} - steckt: {passiv}')
                        passiv = str(ltanks.index(t) + 1)
                        break
                # check if tank exists
                try:
                    passiv_tank = tanks[passiv]
                except KeyError:
                    # Start again, if not
                    print('Tank does not exist!')
                    continue
        
                print(f'\n-> {passiv_tank.name}\n')
        
                ####################################################
                # Check if active tank and passive tank are the same
                if active == passiv:
                    print('Tanks cannot shoots at themselves')
                    sleep(3)
                    continue

        ################################################
        # Check if one of the tanks is already destroyed
        if not active_tank.alive:
            print(f'{active_tank.name} is already destroyed!')
            continue
        elif not passiv_tank.alive:
            print(f'{passiv_tank.name} is already destroyed!')
            continue
    
        print(f'{active_tank.name} is aiming at {passiv_tank.name}\n')
        spinning_cursor(4, 'Calculating...')
        print(f'{active_tank.name} shoots.....\n')

        #################################
        # Check if tank has a malfunction
        sleep(1)
        # spinning_cursor(1, 'Calculating...')
        malfunction = random.randint(1, 101)
        if malfunction <= active_tank.malfunction:
            print(f'{active_tank.name} has a malfunction :(\n')
            sleep(2)
            continue

        ####################
        # Check if tank hits
        treffer = random.randint(1, 101)
        spinning_cursor(3, 'The projectile flies...')
        if treffer <= active_tank.miss:
            print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 20))
            print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 7),
                  Color('{bgmagenta}{white}MISS{/white}{/bgmagenta}'),
                  Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 7))
            print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 20))
            sleep(2)
            continue
        else:
            active_tank.fire_at(passiv_tank)

        # number of alive tanks minus 1 => last one is the winner
        alive_tanks = get_alive_tanks() - 1

        sleep(2)
        # else:
        #     print('Unknown input!')
        #     continue
    elif pvc:
        print('Player vs Computer')
        
        alive_tanks = 0
    else:
        print('ERROR')
        print('this should never occure')

for tank in tanks.values():
    if tank.alive:
        print()
        print(f'{tank.name} is the winner - WOOHOO')
        print()

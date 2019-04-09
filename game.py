#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from time import sleep
import random

from terminaltables import SingleTable
from colorclass import Color, Windows

from tank import *

Windows.enable(auto_colors=True, reset_atexit=True)  # Does nothing if not on Windows.

# TODO: Shop - Done
# TODO: dead tanks can't play - Done
# TODO: vs. Computer - Done - - malfunction missing - Done
# TODO: 2 Players
# TODO: player chooses name - Done
# TODO: choose from predefined tanks
# TODO: dodging
# TODO: network


def get_alive_tanks():
    c = 0
    for tank in tanks.keys():
        c += tanks[tank].alive
    return c


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def shoot(active, target):
    print(f"\n{active.name} is aiming at {target.name}'s tank!\n")
    spinning_cursor(4, 'Calculating...')
    print(f'\n\n{active.name} shoots.....')
    sleep(1)

    # Check if tank has a malfunction
    malfunction = random.randint(1, 101)
    if malfunction <= active.malfunction:
        print(f'\nOh no, {active.name} has a malfunction :(')
        return 'malfunction'
    else:
        return 'shot'


items = {   # 'Item', 'effect', 'value', 'Price', parameter
    '0': ('Cancel', 'Close shop'),
    '1': ('Armor+10', 'Increase armor',    10, 3, 'armor'),
    '2': ('Armor+20', 'Increase armor',    20, 5, 'armor'),
    '3': ('Ammo+2', 'Ammo',                 2, 3, 'ammo'),
    '4': ('Repair', 'Decrease malfunction', 1, 2, 'malfunction'),
    '5': ('item5', 'effect5',               1, 100, 'param5'),
}


def shop(buyer):
    print('\n', str(buyer), '\n')
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
            print('\nCancel...')
            return False
        elif items[item][3] <= buyer.credits:
            print(f'\nYou bought {items[item][0]} for {items[item][3]} credits')
            sleep(2)
            # '1': ('Armor+10', 'Increase armor', 10, 3),
            # '2': ('Armor+20', 'Increase armor', 20, 5),
            # '3': ('Shell+2', '2 shells', 2, 3),
            if item == '1':                    # 10 armor
                buyer.armor += items[item][2]
                print(f'\n{buyer.name} increased his armor by 10.')
            elif item == '2':                  # 20 armor
                buyer.armor += items[item][2]
                print(f'\n{buyer.name} increased his armor by 20.')
            elif item == '3':                  # 2 shells
                buyer.ammo += items[item][2]
                print(f'\n{buyer.name} gets 2 shells.')
            elif item == '4':                  # 2 shells
                buyer.malfunction -= items[item][2]
                print(f'\n{buyer.name} decreased his propability to malfunc by 1.')

            buyer.credits -= items[item][3]
            sleep(2)
            return True
        else:
            print(f'\nYou have not enough credits to buy {items[item][0]}!')
            print(f'{items[item][0]} costs {items[item][3]} credits.')
            print(f'You have {buyer.credits} credits.\n')
            return False
    else:
        print('\nItem does ot exist!')
        sleep(2)
        print('\nGood luck next time!')
        sleep(1)
        return False


def modify_attributes(name):
    factors = {
        'Armor': 5,
        'Ammo': 1,
        'Power': 1,
        'Dmg_mitigation': 1,
    }
    points = 20
    mod_armor, mod_ammo, mod_power, mod_dmg_mitigation = 100, 10, 10, 10
    while points:
        sum = 0
        print(f'\n{name}, your tank has:\n'
              f'Armor:              {mod_armor}  ({factors["Armor"]} armor/p)\n'
              f'Ammo:               {mod_ammo}   ({factors["Ammo"]}1 ammo/p)\n'
              f'Power per shell:    {mod_power}   ({factors["Power"]} power/p)\n'
              f'Damage mitigation:  {mod_dmg_mitigation}   ({factors["Dmg_mitigation"]} dmg_mitigation/p)\n\n'
              f'You can spend {points}p.\n'
              )
        if points:
            mod_armor_points = int(input(f'How many points do want to spend for ARMOR ({points}p)   ({factors["Armor"]} armor/p)?   ') or "0")
            if not mod_armor_points > points:
                points -= mod_armor_points
                mod_armor += (mod_armor_points * factors["Armor"])
                sum += mod_armor_points

        if points:
            mod_ammo_points = int(input(f'How many points do want to spend for AMMO ({points}p)   ({factors["Ammo"]} ammo/p)?   ') or "0")
            if not mod_ammo_points > points:
                points -= mod_ammo_points
                mod_ammo += (mod_ammo_points * factors["Ammo"])
                sum += mod_ammo_points

        if points:
            mod_power_points = int(input(f'How many points do want to spend for POWER PER SHELL ({points}p)   ({factors["Power"]} power/p)?   ') or "0")
            if not mod_power_points > points:
                points -= mod_power_points
                mod_power += (mod_power_points * factors["Power"])
                sum += mod_power_points

        if points:
            mod_dmg_mitigation_points = int(input(f'How many points do want to spend for DAMAGE MITIGATION ({points}p)   ({factors["Dmg_mitigation"]} dmg_mitigation/p)?   ') or "0")
            if not mod_dmg_mitigation_points > points:
                points -= mod_dmg_mitigation_points
                mod_dmg_mitigation += (mod_dmg_mitigation_points * factors["Dmg_mitigation"])
                sum += mod_dmg_mitigation_points

        print(f'\nPoints spent: {sum}')
        # no points left or no points spent
        if not points or not sum:
            print(f'\nOk, {name}, your tank has:\n'
                  f'Armor:              {mod_armor}\n'
                  f'Ammo:               {mod_ammo}\n'
                  f'Power per shell:    {mod_power}\n'
                  f'Damage mitigation:  {mod_dmg_mitigation}\n\n'
                  )
            sleep(4)

            # clear screen
            os.system('cls' if os.name == 'nt' else 'clear')

            return [mod_armor, mod_ammo, mod_power, mod_dmg_mitigation]



##################
##### Instructions
skip = True
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
    mode = input('\nPlayer vs. [P]layer or [C]omputer?  ')
    # Player vs. Player
    if mode.lower() == 'p':
        pvp = True
        num_of_players = int(input(f'\nHow many player?  '))
        players = []
        for i in range(1, num_of_players + 1):
            name_of_player = input(f'\nName of player {i}?  ')
            players.append(name_of_player)

        # clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        tanks = {}
        for counter, player in enumerate(players):
            attributes = modify_attributes(player)
            # tanks[str(counter + 1)] = Tank(player, attributes[0], attributes[1], attributes[2], attributes[3])
            tanks[str(counter + 1)] = Tank(player, *attributes)
    # Player vs. Computer
    elif mode.lower() == 'c':
        pvc = True
        playersturn = True
        playersname = input('\nYour name?  ')
        attributes = modify_attributes(playersname)
        # tanks = {}
        tanks = {'1':  Tank(playersname, *attributes)}
        tanks['2'] = Tank('Computer', 100, 10, 10, 10)
        player_tank = tanks['1']
        computer_tank = tanks['2']
    else:
        mode = False

for tank in tanks.keys():
    print('\n', str(tanks[tank]))

alive_tanks = get_alive_tanks()

ltanks = []
for tank in tanks.keys():
    ltanks.append(tanks[tank].name)

last_player = 0
wait = True
while alive_tanks:

    # Don't clear screen at the beginning
    if not wait:
        # clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
    wait = False

    c = 0
    for tank in tanks.keys():
        c += tanks[tank].alive

    # Create table with tanks
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
        ############ START #############
        # get active and passive tanks #

        if last_player:
            print(f'\nLast Player: {tanks[last_player].name}')

        # get active tank
        active = input('\nActive tank?  ')


        # The player entered a number of a tank
        if represents_int(active[0]):
            if len(active) == 1:
                if active[0] in tanks.keys():
                    last_player = active
                    if not tanks[active[0]].alive:
                        print('\nTank is already destroyed!')
                        sleep(1)
                        print('\nChoose again')
                        sleep(2)
                        continue
                    else:
                        active_tank = tanks[active[0]]
                else:
                    print('\nTank does not exist!')
                    sleep(2)
                    continue

                print(f'\n-> {active_tank.name}\n')

                action = input('Shoot an [E]nemy or go to [S]hop?  ')

                if action.lower() == 's':
                    shop(active_tank)
                    sleep(2)
                    continue
                elif action.lower() == 'e':
                    if active_tank.ammo == 0:
                        print('\nOh no, you have no shells left!')
                        sleep(1)
                        go_to_shop = input('Do you want to buy some? [y/n]  ')
                        if go_to_shop.lower() == 'y':
                            shop(active_tank)
                            sleep(2)
                            continue
                        elif go_to_shop.lower() == 'n':
                            continue
                        else:
                            print('\nWrong input!')
                            sleep(2)
                            continue

                    # get passive tank
                    passive = input('\nTarget?  ')

                    if passive in tanks.keys():
                        passive_tank = tanks[passive]
                        print(f'\n-> {passive_tank.name}')
                    else:
                        print('\nTank does not exist!')
                        sleep(2)
                        continue
                    if active == passive:
                        print('\nTanks cannot shoots at themselves')
                        sleep(2)
                        continue
                    if not passive_tank.alive:
                        print('\nTank is already destroyed!')
                        sleep(2)
                        continue
                else:
                    print('\nWrong input!')
                    sleep(2)
                    continue

            elif len(active) == 2:
                # input = 1s  ->   1 to shop
                if active[0] in tanks.keys() and active[1] == 's':
                    last_player = active[0]
                    if not tanks[active[0]].alive:
                        print('\nTank is already destroyed!')
                        sleep(1)
                        print('\nChoose again')
                        continue
                    else:
                        active_tank = tanks[active[0]]
                        shop(active_tank)
                        sleep(2)
                        continue

                # input = 12  ->   1 shoots 2
                if active[0] in tanks.keys() and active[1] in tanks.keys():
                    last_player = active[0]
                    if not tanks[active[0]].alive or not tanks[active[1]].alive:
                        print('\nOne of these tanks is already destroyed!')
                        sleep(1)
                        print('\nChoose again')
                        sleep(2)
                        continue
                    if active[0] == active[1]:
                        print('\nTanks cannot shoots at themselves')
                        sleep(2)
                        continue
                    else:
                        active_tank = tanks[active[0]]
                        if active_tank.ammo:
                            passive_tank = tanks[active[1]]
                        else:
                            print('\nOh no, you have no shells left!')
                            sleep(1)
                            go_to_shop = input('Do you want to buy some? [y/n]  ')
                            if go_to_shop.lower() == 'y':
                                shop(active_tank)
                                sleep(2)
                                continue
                            elif go_to_shop.lower() == 'n':
                                continue
                            else:
                                print('\nWrong input!')
                                sleep(2)
                                continue
                else:
                    print('\nOne of these tanks does not exist!')
                    sleep(1)
                    print('\nChoose again')
                    sleep(2)
                    continue

            else:
                print('\nWrong input!')
                sleep(2)
                continue
        else:
            print('\nWrong input!')
            sleep(2)
            continue

        shot = shoot(active_tank, passive_tank)
        # Tank has a malfunction
        if shot == 'malfunction':
            sleep(2)
            continue
        else:
            active_tank.fire_at(passive_tank)

    elif pvc:
        # It's player's turn
        if playersturn:
            print(f"\nIt's {player_tank.name}'s turn")
            sleep(0.5)
            action = 'e' #input('\nShoot the [E]nemy or go to the [S]hop?  ')
            if action.lower() == 'e':
                print(f'\n{player_tank.name} shoots...')
                shot = shoot(player_tank, computer_tank)
                # Tank has a malfunction
                if shot == 'malfunction':
                    playersturn = not playersturn
                    sleep(2)
                    continue
                # Tank missed the enemy
                if shot == 'miss':
                    playersturn = not playersturn
                    sleep(1)
                    continue
                # Tank hits
                else:
                    player_tank.fire_at(computer_tank)
            elif action.lower() == 's':
                shop(player_tank)
                sleep(2)
                # Player can shoot after shop
                # playersturn = not playersturn
                continue
            else:
                print('\nUnknown input!')
                sleep(2)
                continue
        # It's computer's turn
        else:
            print("It's computer's turn")
            shot = shoot(computer_tank, player_tank)
            # Tank has a malfunction
            if shot == 'malfunction':
                playersturn = not playersturn
                sleep(1)
                continue
            # Tank missed the enemy
            if shot == 'miss':
                playersturn = not playersturn
                sleep(1)
                continue
            # Tank hits
            else:
                computer_tank.fire_at(player_tank)

        playersturn = not playersturn
    else:
        print('ERROR')
        print('this should never occure')

    # number of alive tanks minus 1 => last one is the winner
    alive_tanks = get_alive_tanks() - 1
    sleep(2)

for tank in tanks.values():
    if pvc:
        # If player is next, Computer won
        if playersturn:
            print('\nOh no, you loose!\nComputer wins!')
        else:
            print('\nYOU win!')
    else:
        if tank.alive:
            print()
            print(f'{tank.name} is the winner - WOOHOO')
            print()

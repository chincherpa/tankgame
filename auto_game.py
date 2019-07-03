#!/usr/bin/env python
# -*- coding: utf-8 -*-

ANZAHL = 10000

import os
from random import randint

from terminaltables import SingleTable
from colorclass import Windows

from auto_tank import *

Windows.enable(auto_colors=True, reset_atexit=True)  # Does nothing if not on Windows.

items = {# 'Item',    'effect',              value,   Price, parameter
    '1': ('Armor+10', 'Increase armor',      10,      3,     'armor'),
    '2': ('Armor+20', 'Increase armor',      20,      5,     'armor'),
    '3': ('Ammo+2',   'Ammo',                 2,      3,     'ammo'),
    '4': ('Repair',   'Decrease malfunction', 1,      2,     'malfunction'),
}

predefined_tanks = {# Name,  (mod_armor, mod_ammo, mod_power, mod_dmg_mitigation)
    '1': ('Heavy Tank',      (135, 13, 15, 15)),
    '2': ('Middle Tank',     (125, 17, 14, 14)),
    '3': ('Light Tank',      (115, 21, 13, 13)),
    '4': ('UltraLight Tank', (105, 25, 12, 12)),
}

def select_tank(choice):
    return predefined_tanks[str(choice)][0], predefined_tanks[str(choice)][1]
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
    # print(f"\n{active.name} is aiming at {target.name}'s tank!\n")
    if not DEBUG: spinning_cursor(4, 'Calculating...')
    # print(f'\n\n{active.name} shoots.....')
    if not DEBUG: sleep(1)

    # Check if tank has a malfunction
    malfunction = random.randint(1, 101)
    if malfunction <= active.malfunction:
        active.malfuncs += 1
        # print(f'\nOh no, {active.name} has a malfunction :(')
        return 'malfunction'
    else:
        return 'shot'
def get_4_randoms(sum):
    
    rnd_sum = 0
    while rnd_sum != sum:
        r1 = randint(0, sum)
        r2 = randint(0, sum)
        r3 = randint(0, sum)
        r4 = randint(0, sum)
        rnd_sum = r1 + r2 + r3 + r4

    return r1, r2, r3, r4
def random_tank():
    factors = {
        'Armor': 3,
        'Ammo': 1,
        'Power': 1,
        'Dmg_mitigation': 2,
    }
    
    points = 20
    rnd_armor, rnd_ammo, rnd_power, rnd_dmg_mit = get_4_randoms(points)
    
    mod_armor, mod_ammo, mod_power, mod_dmg_mitigation = 100, 10, 10, 10
    mod_armor += (rnd_armor * factors["Armor"])
    mod_ammo += (rnd_ammo * factors["Ammo"])
    mod_power += (rnd_power * factors["Power"])
    mod_dmg_mitigation += (rnd_dmg_mit * factors["Dmg_mitigation"])

    return [mod_armor, mod_ammo, mod_power, mod_dmg_mitigation]
def dont_shoot(player):
    player.credits += 1
    # print(f'{player.name} waits and earns 1 credit.')
    sleep(2)
def get_action():
    return input('Shoot an [E]nemy, go to [S]hop or do [N]othing (+ 1 credit)?  ')

for j in range(1, 5):
    loop = 0
    playerwins = 0
    computerwins = 0
    predefined_tank_input = j
    tankname, v = select_tank(predefined_tank_input)
    print(tankname)
    #print(v)

    for i in range(ANZAHL):
        loop += 1
        
        if i%1000 == 0:
            p_com = int((computerwins/loop)*100)
            p_pla = int((playerwins/loop)*100)
            print(f'running... {i} ({p_com}:{p_pla}) ')

        tanks = {}

        # Player vs. Computer
        playersturn = True
        playersname = 'DEBUGGER'
        tankname, attributes = select_tank(predefined_tank_input)

        tanks = {'1':  Tank(playersname, *attributes)}

        armor, ammo, power, dmg_miti = random_tank()
        tanks['2'] = Tank('Computer', armor, ammo, power, dmg_miti)

        player_tank = tanks['1']
        computer_tank = tanks['2']

        #print('', armor, ammo, power, dmg_miti)

        alive_tanks = get_alive_tanks()

        ltanks = []
        for tank in tanks.keys():
            ltanks.append(tanks[tank].name)

        last_player = 0
        wait = True
        while alive_tanks:

            c = 0
            for tank in tanks.keys():
                c += tanks[tank].alive

            # It's player's turn
            if playersturn:
                if not DEBUG: sleep(0.5)

                if DEBUG:
                    action = 'e'
                else:
                    action = get_action()

                if action.lower() == 'e':
                    # print(f'\n{player_tank.name} shoots...')
                    shot = shoot(player_tank, computer_tank)
                    # Tank has a malfunction
                    if shot == 'malfunction':
                        if not DEBUG: sleep(2)
                    # Tank missed the enemy
                    if shot == 'miss':
                        if not DEBUG: sleep(1)
                    # Tank hits
                    else:
                        player_tank.fire_at(computer_tank)
                elif action.lower() == 's':
                    shop(player_tank)
                    if not DEBUG: sleep(2)
                    # Player can shoot after shop
                elif action.lower() == 'n':
                    dont_shoot(player_tank)
                else:
                    # print('\nUnknown input!')
                    sleep(0.5)
                    # print('\nTry again...')
                    if not DEBUG: sleep(1)

                if action.lower() in 'en':
                    # Player can shoot after shop
                    # else Computer is next
                    playersturn = False

            # It's computer's turn
            else:
                shot = shoot(computer_tank, player_tank)
                # Tank has a malfunction
                if shot == 'malfunction':
                    playersturn = True
                    if not DEBUG: sleep(1)
                    continue
                # Tank missed the enemy
                if shot == 'miss':
                    playersturn = True
                    if not DEBUG: sleep(0)
                    continue
                # Tank hits
                else:
                    computer_tank.fire_at(player_tank)

                playersturn = True

            # number of alive tanks minus 1 => last one is the winner
            alive_tanks = get_alive_tanks() - 1
            if not DEBUG: sleep(2)

        for tank in tanks.values():
            # If player is next, Computer won
            if playersturn:
                # print('\nComputer wins!')
                computerwins += 1
                break
            else:
                # print('\nPlayer wins!')
                playerwins += 1
                break

        # if i % 100000 == 0:
            # print('               computerwins:', computerwins)
            # print('               playerwins  :', playerwins, '\n')

    p_com = int((computerwins/ANZAHL)*100)
    p_pla = int((playerwins/ANZAHL)*100)

    print('-----------------------------------')
    print('               computerwins:', computerwins, f'({p_com}%)')
    print('               playerwins  :', playerwins, f'({p_pla}%)', '\n')

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from time import sleep
import random

from terminaltables import SingleTable
from crayons import yellow, red  # green, 

from tank import *

#GITHUB-TEST

DEBUG = False

# huhu
# TODO: Shop - Done
# TODO: dead tanks can't play - Done
# TODO: vs. Computer - Done - - malfunction missing - Done
# TODO: player chooses name - DONE
# TODO: choose from predefined tanks - DONE
# TODO: computer gets random tank - DONE
# TODO: 2 Players - Done

# TODO: dodging
# TODO: network

items = {  # 'Item',  'effect',         value, Price, parameter
  '1': ('Armor+10', 'Increase armor',      10,     3, 'armor'),
  '2': ('Armor+20', 'Increase armor',      20,     5, 'armor'),
  '3': ('Ammo+2',   'Ammo',                 2,     3, 'ammo'),
  '4': ('Repair',   'Decrease malfunction', 1,     2, 'malfunction'),
}

predefined_tanks = {  # Name,(armor, ammo, power, dmg_mitigation)
  '1': ('Heavy Tank',    (120,    7,  15, 13)),
  '2': ('Middle Tank',   (110,    9,  14, 11)),
  '3': ('Light Tank',    (95,    11,  12,  9)),
  '4': ('UltraLight Tank', (80,    15,  10,  7)),
}


def spinning_cursor(duration, value=None):
  for _ in range(duration):
    for cursor in '|/-\\':
      sleep(0.1)
      sys.stdout.write(f'\r{cursor} {value}')
      sys.stdout.flush()


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
  if not DEBUG:
    spinning_cursor(4, 'Calculating...')
  print(f'\n\n{active.name} shoots.....')
  if not DEBUG:
    sleep(1)

  # Check if tank has a malfunction
  malfunction = random.randint(1, 101)
  if malfunction <= active.malfunction:
    active.malfuncs += 1
    print(f'\nOh no, {active.name} has a malfunction :(')
    return 'malfunction'
  else:
    return 'shot'


def shop(player):
  print()
  print(str(player), '\n')
  try:
    shop_table = [['#', 'Item',    'Effect',    ' Value',    'Price'],        # Header
            ['1', items['1'][0], items['1'][1], items['1'][2], items['1'][3]],    # Armor+10
            ['2', items['2'][0], items['2'][1], items['2'][2], items['2'][3]],    # Armor+20
            ['3', items['3'][0], items['3'][1], items['3'][2], items['3'][3]],    # Ammo+2
          #   ['4', items['4'][0], items['4'][1], items['4'][2], items['4'][3]],     # item4
            ['-', '---', '---', '---', '---', '---'],                 # item5
            ['0', 'Cancel']]                              # Cancel

    shop_table_instance = SingleTable(shop_table, 'Shop')
    # for i in range(2, 60):
    #   shop_table_instance.justify_columns[i] = 'center'
    print(shop_table_instance.table)
  except KeyError as e:
    print('------------------------------------------------')
    print(f'Error: {e.name}')
    print('------------------------------------------------')

  item = input('\nWhat do you want to buy?\t')

  if int(item) in range(len(items)):
    if item == '0':
      print('\nCanceling...')
      sleep(1)
      return False
    elif items[item][3] <= player.credits:
      print(f'\nYou bought {items[item][0]} for {items[item][3]} credits')
      sleep(2)
      # '1': ('Armor+10', 'Increase armor', 10, 3),
      # '2': ('Armor+20', 'Increase armor', 20, 5),
      # '3': ('Shell+2', '2 shells', 2, 3),
      if item == '1':          # 10 armor
        player.armor += items[item][2]
        print(f'\n{player.name} increased his armor by 10.')
      elif item == '2':          # 20 armor
        player.armor += items[item][2]
        print(f'\n{player.name} increased his armor by 20.')
      elif item == '3':          # 2 shells
        player.ammo += items[item][2]
        print(f'\n{player.name} gets 2 shells.')
      elif item == '4':          # 2 shells
        player.malfunction -= items[item][2]
        print(f'\n{player.name} decreased his propability to malfunc by 1.')

      player.credits -= items[item][3]
      if not DEBUG:
        sleep(2)
      return True
    else:
      print(f'\nYou have not enough credits to buy {items[item][0]}!')
      print(f'{items[item][0]} costs {items[item][3]} credits.')
      print(f'You have {player.credits} credits.\n')
      return False
  else:
    print('\nItem does not exist!')
    print('\nGood luck next time!')
    sleep(2)
    return False


def modify_attributes(player):
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
    print(f'\n{player}, your tank has:\n'
        f'Armor:        {mod_armor}  ({factors["Armor"]} armor/p)\n'
        f'Ammo:         {mod_ammo}   ({factors["Ammo"]}1 ammo/p)\n'
        f'Power per shell:  {mod_power}   ({factors["Power"]} power/p)\n'
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
      print(f'\nOk, {player}, your tank has:\n'
          f'Armor:        {mod_armor}\n'
          f'Ammo:         {mod_ammo}\n'
          f'Power per shell:  {mod_power}\n'
          f'Damage mitigation:  {mod_dmg_mitigation}\n\n'
          )
      sleep(4)

      # clear screen
      os.system('cls' if os.name == 'nt' else 'clear')

      return [mod_armor, mod_ammo, mod_power, mod_dmg_mitigation]


def select_tank():
  while True:
    print('\nAvailable tanks:\n')
    try:
      tank_table = [['#', 'NAME', 'Armor', 'Ammo', 'Power', 'Damage\nmitigation']]
      for entry in range(1, len(predefined_tanks) + 1):
        temp = []
        temp = [str(entry), predefined_tanks[str(entry)][0]]
        for i in range(len(predefined_tanks[str(entry)][1])):
          temp.append(predefined_tanks[str(entry)][1][i])
        tank_table.append(temp)

      tank_table.append(['-', '---', '---', '---', '---', '---'])
      tank_table.append(['0', 'Cancel'])

      tank_table_instance = SingleTable(tank_table, 'Select tank')
      # for i in range(2, 60):
      #   shop_table_instance.justify_columns[i] = 'center'
      print(tank_table_instance.table)
    except KeyError as e:
      print('------------------------------------------------')
      print(f'Error: {e.name}')
      print('------------------------------------------------')

    predefined_tank = input("\nSelect a tank\t") or 0

    if predefined_tank:
      if int(predefined_tank) in range(len(predefined_tanks)):
        print(predefined_tanks[predefined_tank])
        break
      else:
        print('\nTank does not exist!')
        print('\nGood luck next time!')
        sleep(2)

  return predefined_tanks[predefined_tank][1]


def get_4_randoms(sum):
  rnd_sum = 0
  while rnd_sum != sum:
    r1 = random.randint(0, sum)
    r2 = random.randint(0, sum)
    r3 = random.randint(0, sum)
    r4 = random.randint(0, sum)
    rnd_sum = r1 + r2 + r3 + r4

  return r1, r2, r3, r4


def random_tank():
  factors = {
    'Armor': 5,
    'Ammo': 1,
    'Power': 1,
    'Dmg_mitigation': 1,
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
  print(f'{player.name} waits and earns 1 credit.')
  sleep(2)


##################
# Instructions
skip = True
if not skip:
  print('\n\nInstructions:\n\n'
      'Every tank has these attributes:\n'
      '  - name       : Name of the tank/player\n'
      '  - armor      : amount of armor, decreased (-damage) when hit (min = 0)\n'
      '  - ammo       : amount of shells, -1 per shot\n'
      '  - power      : damage per shell\n'
      '  - alive      : is tank alive?, starts with TRUE\n'
      '  - dmg_mitigation : Mitigation of incoming damage, -1 per hit (min = 0)\n'
      '  - credits    : amount of credits, starts with ' + str(SETTINGS['credits']) + '\n'
      '\n'
      '  --- SETTINGS ---\n'
      '  - miss       : tanks can miss by ' + str(SETTINGS['probability_to_miss']) + '%\n'
      '  - malfunction  : tanks can have malfunction by ' + str(
    SETTINGS['probability_of_malfunction']) + '%, increased by 1 when hit\n\n'
    )

  input('Press ENTER to start...')
else:
  print('\n\nInstructions skipped\n')

mode = False
pvp = False
pvc = False
while not mode:
  if DEBUG:
    mode = 'p'
  else:
    mode = input('\nPlayer vs. [P]layer or [C]omputer?\t')

  tanks = {}

  # Player vs. Player
  if mode.lower() == 'p':
    pvp = True
    num_of_players = int(input('\nHow many player?\t'))
    # Toggle Players: https://stackoverflow.com/questions/8381735/how-to-toggle-a-value-in-python
    if num_of_players == 2:
      active = 2
      passive = 3
      total = 3
    players = []
    for i in range(1, num_of_players + 1):
      name_of_player = input(f'\nName of player {i}?\t')
      players.append(name_of_player)

    # clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

    for counter, playersname in enumerate(players):
      choice = None
      while choice is None:
        choice = input(f'\n{playersname}: Select [P]redefined tank or [M]odify your own?\t')
        if choice.lower() == 'm':
          attributes = modify_attributes(playersname)
        elif choice.lower() == 'p':
          attributes = select_tank()
          if attributes is False:
            choice = None
        else:
          choice = None

      # tanks[str(counter + 1)] = Tank(playersname, attributes[0], attributes[1], attributes[2], attributes[3])
      tanks[str(counter + 1)] = Tank(playersname, *attributes)

  # Player vs. Computer
  elif mode.lower() == 'c':
    pvc = True
    playersturn = True
    if DEBUG:
      playersname = 'DEBUGGER'
      # attributes = [130, 18, 12, 15]
      # tanks = {'1':  Tank(playersname, *attributes)}
      # tanks['2'] = Tank('Computer', 125, 15, 15, 15)
    else:
      playersname = input('\nYour name?\t')

    choice = None
    while choice is None:
      choice = input('\nSelect [P]redefined tank or [M]odify your own?\t')
      if choice.lower() == 'm':
        attributes = modify_attributes(playersname)
      elif choice.lower() == 'p':
        attributes = select_tank()
        if attributes is False:
          choice = None
      else:
        choice = None

    # tanks = {}
    tanks = {'1': Tank(playersname, *attributes)}
    spinning_cursor(3, "generating Computer's tank...")
    print('\n\n')
    armor, ammo, power, dmg_miti = random_tank()
    tanks['2'] = Tank('Computer', armor, ammo, power, dmg_miti)

    player_tank = tanks['1']
    computer_tank = tanks['2']
  else:
    mode = False

for tank in tanks.keys():
  print(str(tanks[tank]), '\n')

alive_tanks = get_alive_tanks()

ltanks = []
for tank in tanks.keys():
  ltanks.append(tanks[tank].name)

last_player = 0
wait = True
while alive_tanks:

  # # Don't clear screen at the beginning
  # if not wait:
  #   # clear screen
  #   os.system('cls' if os.name == 'nt' else 'clear')
  # wait = False

  os.system('cls' if os.name == 'nt' else 'clear')

  c = 0
  for tank in tanks.keys():
    c += tanks[tank].alive

  # Create table with tanks
  tank_table = [['#', 'Name', 'Armor', 'Ammo', 'Power', 'Dmg red.', 'Miss', 'Malf.', 'Credits', 'Misses']]
  counter = 1
  for tank in tanks.keys():
    name = tanks[tank].name
    # if tanks[tank].alive:
    #   name = green(tanks[tank].name)
    # else:
    #   name = red(tanks[tank].name)

    armor = tanks[tank].armor
    # if tanks[tank].armor < 51:
    #   armor = yellow(tanks[tank].armor)
    # if tanks[tank].armor < 26:
    #   armor = red(tanks[tank].armor)

    ttable_row = [counter, name, armor, tanks[tank].ammo, tanks[tank].power, tanks[tank].dmg_mitigation,
        tanks[tank].miss, tanks[tank].malfunction, tanks[tank].credits, tanks[tank].misses]
    tank_table.append(ttable_row)
    counter += 1
  table_instance = SingleTable(tank_table, 'Tanks')
  for i in range(2, len(tank_table[0])):
    table_instance.justify_columns[i] = 'center'
  print(table_instance.table)

  if pvp:
############ START #############
# get active and passive tanks #

    if last_player:
      print(f'\nLast Player: {tanks[last_player].name}')

    # get active tank
    if num_of_players == 2:
      # Toggle zwischen 1 und 2
      active = str(total - int(active))
    else:
      active = input('\nActive tank?\t')

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

        s = '[S]hoot an enemy, [B]uy something or do [N]othing (+ 1 credit)?\t'
        action = input(s)

        if action.lower() == 'b':
          shop(active_tank)
          sleep(2)
          continue
        elif action.lower() == 's':
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
          if num_of_players == 2:
            # Toggle zwischen 1 und 2
            passive = str(total - int(active))
          else:
            passive = input('\nTarget?\t')

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
        elif action.lower() == 'n':
          dont_shoot(active_tank)
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
      print(f"\nIt's {player_tank.name}'s turn\n")
      if not DEBUG:
        sleep(0.5)

      if DEBUG:
        action = 'e'
      else:
        s = '[S]hoot an enemy, [B]uy something or do [N]othing (+ 1 credit)?\t'
        action = input(s)

      if action.lower() == 's':
        print(f'\n{player_tank.name} shoots...')
        shot = shoot(player_tank, computer_tank)
        # Tank has a malfunction
        if shot == 'malfunction':
          if not DEBUG:
            sleep(2)
        # Tank misses the enemy
        elif shot == 'miss':
          if not DEBUG:
            sleep(1)
        # Tank hits
        else:
          player_tank.fire_at(computer_tank)
      elif action.lower() == 'b':
        shop(player_tank)
        if not DEBUG:
          sleep(2)
        # Player can shoot after shop
      elif action.lower() == 'n':
        dont_shoot(player_tank)
      else:
        print('\nUnknown input!')
        sleep(0.5)
        print('\nTry again...')
        if not DEBUG:
          sleep(1)

      if action.lower() in 'en':
        # Player can shoot after shop
        # else Computer is next
        playersturn = False

    # It's computer's turn
    else:
      print("\nIt's computer's turn")
      shot = shoot(computer_tank, player_tank)
      # Tank has a malfunction
      if shot == 'malfunction':
        playersturn = True
        if not DEBUG:
          sleep(1)
        continue
      # Tank missed the enemy
      if shot == 'miss':
        playersturn = True
        if not DEBUG:
          sleep(0)
        continue
      # Tank hits
      else:
        computer_tank.fire_at(player_tank)

      playersturn = True

  else:
    print('ERROR')
    print('this should never occure')

  # number of alive tanks minus 1 => last one is the winner
  alive_tanks = get_alive_tanks() - 1
  if not DEBUG:
    sleep(2)

for tank in tanks.values():
  if pvc:
    # If player is next, Computer won
    if playersturn:
      print('\nOh no, you loose!\nComputer wins!')
      break
    else:
      print('\nYOU win!')
      break
  else:
    if tank.alive:
      print()
      print(f'{tank.name} is the winner - WOOHOO')
      print()
      break

print()

# Create table with tanks
tank_table = [['#', 'Name', 'Armor', 'Ammo', 'Power', 'Dmg red.', 'Miss', 'Malf.', 'Credits', 'shots', 'hits', 'misses', 'malfuncs', 'dmg']]
counter = 1
for tank in tanks.keys():
  if tanks[tank].alive:
    name = yellow(tanks[tank].name)
  else:
    name = red(tanks[tank].name)

  armor = tanks[tank].armor
  if tanks[tank].armor < 51:
    armor = yellow(tanks[tank].armor)
  if tanks[tank].armor < 26:
    armor = red(tanks[tank].armor)

  tank_table.append(
      [counter, name, armor, tanks[tank].ammo, tanks[tank].power, tanks[tank].dmg_mitigation, tanks[tank].miss,
      tanks[tank].malfunction, tanks[tank].credits, tanks[tank].shots, tanks[tank].hits, tanks[tank].misses, tanks[tank].malfuncs, tanks[tank].dmg])
  counter += 1
table_instance = SingleTable(tank_table, 'Tanks')
for i in range(2, 60):
  table_instance.justify_columns[i] = 'center'
print(table_instance.table)

input('Press Enter')

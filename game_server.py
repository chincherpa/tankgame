#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
##########################################################################################
##      FyreFly Messaging, Server Framework
##
##      Version 0.1a
##      Copyright (C) 2019 - Aaron Edwards
##
##      Email: edwardsaaron94@gmail.com
##
##      This program is built in Python 3.5.1 (v3.5.1:37a07cee5969, Dec  6 2015, 01:38:48)
##
##########################################################################################

######################################## IMPORTS #########################################

## @Socket is used for low-level networking interfaces.
## @Threading is used for handling multiple tasks at once. Clients/Connections/Cmds
## @os is being used for clearing the screen, and a killing a thread... not the best idea I know :/
## @time is being used for nothing as of yet but will be implemented for something at some stage.
import socket
from _thread import *
import threading
import os
import time

######################################## GLOBALS #########################################

## These are the global variables used by the server.
## HOST is '' so when the socket.bind() function is called it will attach to the localhost.
## PORT is the port the server will be running on.
##      PORT can be any port you choose.
## BUFFER_SIZE is used by socket.recv() to determine the max amount of data
##      allowed to pass through the socket.
## ADDR is just a tuple of HOST,PORT to make the socket.bind() function easier to read.

HOST = ''
PORT = 33000
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)

## These two dictionaries are used to store information about a client
## @CLIENTS holds {socket: client_name}
## @ADDRESSES hold {socket: (IP, PORT)}

CLIENTS = {}
ADDRESSES = {}

## The General Banner Header for start up and clear screen.
BANNER = '''
#################################################
##                                             ##
##         FyreFly Messaging - SERVER          ##
##                                             ##
##                Version 0.1a                 ##
##     Copyright (C) 2019 - Aaron Edwards      ##
##                                             ##
##       Email: edwardsaaron94@gmail.com       ##
##                                             ##
#################################################\n
[*] Type 'help' to see a list of available server commands.'''

## This creates a server socket on startup and binds it to the (HOST,PORT) a.k.a. ADDR.
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

######################################### FUNCTIONS #########################################

## This thread is always running to check whether new connections have been established
## By the client applications.
def accept_connections():

    ## This generates a new thread for the server menu commands and starts it.
    MENU_THREAD = threading.Thread(target=server_cmds)
    MENU_THREAD.start()

    ## Always waiting to accept the new connections.
    ## Will be updated to only accept a certain connection limit.
    while True:

        ## This accepts a message and creates a socket object and tuple which is the
        ## Clients IP and Port numbers.
        ## Then a message is printed to the server terminal telling the User that a new
        ## Connection has been made.
        client_socket, client_address = SERVER.accept()
        print("[*] {}:{} has connected.".format(client_address[0], client_address[1]))

        ## Once the client connectivity has been established, the server will send client
        ## A message to welcome them to the server, and also a request to get their name
        ## For use in the chat room
        client_socket.send("[*] Greetings! Welcome to FyreFly!\n[*] Please enter your name to get started.".encode())

        ## This section adds the relevant socket information to the ADDRESSES
        ## dictionary = (<IP>,<PORT>).
        ## After that a new thread for handling that client is generated and started.
        ADDRESSES[client_socket] = client_address
        CLIENT_THREAD = threading.Thread(target=handle_client, args=(client_socket,))
        CLIENT_THREAD.start()


## This is the thread that listens for all incoming data by a single client.
def handle_client(client):

    ## Initially gets the name the client sends after loading the application and connecting
    ## To the server and welcomes them to the chat room.
    client_name = client.recv(BUFFER_SIZE).decode()
    client.send("\n[*] Welcome {}!\n[*] If you ever want to exit: type <quit> in the chat.".format(client_name).encode())

    ## This calls the broadcast function to notify Who has joined the chat room.
    message = "\n[*] {} Has joined the chat room!".format(client_name)
    broadcast(message)

    ## This adds the clients name to the CLIENTS dictionary
    CLIENTS[client] = client_name

    ## After the above steps are finished it will forever loop until the user
    ## Sends a request to quit.
    while True:
        ## This tries to constantly listen for data being sent over the connected client Socket
        try:
            message = client.recv(BUFFER_SIZE).decode()

            ## Once the user has sent a message, the server will check to see if it is not
            ## A <quit> request. If it is not it will call the broadcast function to send
            ## The clients message into the chatroom. If it is a <quit> request it will
            ## Call the close_connection function and drop the user from the server and
            ## Close the thread.
            if message != "<quit>":
                broadcast(message, "\n"+client_name+': ')
            else:
                close_connection(client)
                break
        except:
            continue


## This is called after every message has been received by a client.
## It will send a message to all clients in the CLIENTS dictionary
## And format the broadcast with the clients name followed by the message.
def broadcast(message, prefix=''):
    try:
        for user in CLIENTS:
            user.send("{}{}".format(prefix, message).encode())
    except:
        pass


## This function is called any time a Client or Connection needs to be closed
## It will receive a kicked=bool argument to check it was server or client initiated.
def close_connection(client, kicked=False):

    ## This is for when a client initiates a connection close request from chat.
    ## It will send the <quit> message to the client telling them it is okay to quit.
    ## It also notifies the chat room who has left.
    ## It notifies the server User too on Who:IP:Port has disconnected.
    if not kicked:
        client.send("<quit>".encode())
        broadcast("\n[*] {} has left the chat room.".format(CLIENTS[client]))
        print('[*] Client: \'{}\' ~ {} : {} Has disconnected.'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))

    ## This is for when the server User initiates the kick command
    ## It will print to the server that the user has been kicked successfully
    else:
        print('[*] Client: \'{}\' ~ {} : {} Has been kicked.'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))

    ## This closes the requested client connection.
    ## And removes it from the ADDRESSES/CLIENTS dictionaries so
    ## It wont show as a current connection anymore.
    client.close()
    del ADDRESSES[client]
    del CLIENTS[client]


## This thread deals with the Menu operations/commands of the server while all Clients
## And connections are being dealt with in different threads.
def server_cmds():
    while True:
        ## Gets an option from the User and goes through various IF/ELIF statements
        ## Depending on input.
        cmd = input('>> ')

        ## This option just shows a list of all the available server commands.
        if cmd.lower() == 'help':
            print('[*] BC - Broadcast a message to the chat room.')
            print('[*] CLS - Clear the screen.')
            print('[*] HELP - Provides Help information for Server Commands.')
            print('[*] KICK - Kick a client from the server.')
            print('[*] LS - Lists the current connections.')

        ## This option allows the User of the server terminal to send a message directly into
        ## The chat room for everyone to see. The Clients will see: SERVER: <message>
        elif cmd.lower() == 'bc':
            message = input('What would you like to broadcast?\n>> ')
            broadcast(message, "\nSERVER: ")

        ## The User can clear the screen on the server terminal whenever they like and the banner
        ## Will always be displayed after clearing.
        elif cmd.lower() == 'cls':
            os.system('cls')
            print(BANNER)

        ## This command allows the User to get a list of all the active clients in the chat room
        ## And all the connections that havent made a name to enter the chat yet (base connection).
        elif cmd.lower() == 'ls':
            for client in ADDRESSES:
                try:
                    print('[*] Client: \'{}\' ~ {} : {}'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))
                except:
                    print('[*] Connection: {} : {}'.format(ADDRESSES[client][0], ADDRESSES[client][1]))

        ## If the User decides to kick a person from the chat for whatever reason the server
        ## Will loop through all the clients connected to the room only.
        ## If the server finds a connection that isnt in the chat it will skip it and move on until
        ## All objects are checked.
        elif cmd.lower() == 'kick':
            print('[*] Who would you like to kick from chat?\n')
            i = 0
            connection = []
            for client in ADDRESSES:
                try:
                    print('[{}] {}'.format(i+1, CLIENTS[client]))
                    i += 1
                    connection.append(client)
                except:
                    continue

            ## The User will pick a number from the list of active clients in the chat room
            ## That client will have a message sent to them and then the client socket is then
            ## closed and removes that object using close_connection.
            kick = input('\n>> ')
            try:
                connection[int(kick)-1].send('\n[*] Sorry but you have been kicked from the server. \n[*] The Server Admin obviously doesnt like you. :('.encode())
                broadcast('\n[*] {} Has been kicked from the server!'.format(CLIENTS[connection[int(kick)-1]]))
                close_connection(connection[int(kick)-1], kicked=True)
            except:
                print("[*] Cannot close connection!")

        ## When the User decides to quit the Server Application
        ## It loops through all the currently connected clients and closes each socket
        ## It will loop through clients in the chat, and also clients that are just base connected
        elif cmd.lower() == 'quit':
            for client in ADDRESSES:
                try:
                    print('[*] Closing Client: \'{}\' ~ {} : {}'.format(CLIENTS[client], ADDRESSES[client][0], ADDRESSES[client][1]))
                except:
                    print('[*] Closing Connection: {} : {}'.format(ADDRESSES[client][0], ADDRESSES[client][1]))
                client.close()
            os._exit(1)

        ## If the User doesnt type a valid command it will tell them.
        elif cmd != '':
            print('[*] Not a valid server command')


## Puts the server into listening mode
## Starts the thread on accepting all client connections to the server.
def Main():
    SERVER.listen(5)
    ACCEPT_THREAD = threading.Thread(target=accept_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()


## Clear the screen on start and display the main Banner.
## Then jumps to the main TCP related stuff.
if __name__ == '__main__':
    os.system('cls')
    print(BANNER)
    Main()


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################





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


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def shoot(active, target):
    print(f'{active.name} is aiming at {target.name}\n')
    spinning_cursor(4, 'Calculating...')
    print(f'{active.name} shoots.....\n')

    #################################
    # Check if tank has a malfunction
    sleep(1)
    malfunction = random.randint(1, 101)
    if malfunction <= active.malfunction:
        print(f'Oh no, {active.name} has a malfunction :(\n')
        return 'malfunction'

    ####################
    # Check if tank hits
    treffer = random.randint(1, 101)
    spinning_cursor(3, 'The projectile flies...')
    if treffer <= active.miss:
        print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 20))
        print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 7),
              Color('{bgmagenta}{white}MISS{/white}{/bgmagenta}'),
              Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 7))
        print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 20))
        sleep(2)
        return 'miss'
    else:
        return 'hit'


items = {   # 'Item', 'effect', 'value', 'Price', parameter
    '0': ('Cancel', 'Close shop'),
    '1': ('Armor+10', 'Increase armor',    10, 3, 'armor'),
    '2': ('Armor+20', 'Increase armor',    20, 5, 'armor'),
    '3': ('Ammo+2', 'Ammo',                 2, 3, 'ammo'),
    '4': ('Repair', 'Decrease malfunction', 1, 2, 'malfunction'),
    '5': ('item5', 'effect5',               1, 100, 'param5'),
}


def shop(buyer):
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
    print('')

    if item in '01234':
        if item == '0':
            print('Cancel...')
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
    mode = input('\nPlayer vs. [P]layer or [C]omputer?  ')
    if mode.lower() == 'p':
        pvp = True
        tanks = {     # NAME    armor|ammo|power|dmg_mitigation %
            '1': Tank('Björn',  10,  10,  12,   15),
            '2': Tank('Lutz',   50,   13,  12,   18),
            '3': Tank('Martin', 100,  10,  13,   16),
        }
    elif mode.lower() == 'c':
        pvc = True
        playersturn = True
        playersname = input('\nHow do you want to be called?  ')
        tanks = {     # NAME      armor|ammo|power|dmg_mitigation %
            'p': Tank(playersname, 120,  10,  12,   15),
            'c': Tank('Computer',  90,  13,  12,   18),
        }
        player_tank = tanks['p']
        computer_tank = tanks['c']
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
    # print(f'alive_tanks: {alive_tanks}')
    # print(f'mode: {mode}')
    # print(f'pvp: {pvp}')
    # print(f'pvc: {pvc}')
    # print(f'playersturn: {playersturn}')
    # print('\n')

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
        ############ START #############
        # get active and passive tanks #

        #################
        # get active tank
        active = input('Active tank?  ')

        #######################################
        # The player entered a number of a tank
        if represents_int(active[0]):
            if len(active) == 1:
                if active[0] in tanks.keys():
                    if not tanks[active[0]].alive:
                        print('Tank is already destroyed!')
                        sleep(1)
                        print('Choose again')
                        sleep(2)
                        continue
                    else:
                        active_tank = tanks[active[0]]
                else:
                    print('Tank does not exist!')
                    sleep(3)
                    continue

                print(f'\n-> {active_tank.name}\n')

                action = input('Shoot an [E]nemy or go to [S]hop?  ')

                if action.lower() == 's':
                    shop(active_tank)
                    sleep(2)
                    continue
                elif action.lower() == 'e':
                    ##################
                    # get passive tank
                    passive = input('Target?  ')

                    if passive in tanks.keys():
                        passive_tank = tanks[passive]
                        print(f'\n-> {passive_tank.name}\n')
                    else:
                        print('Tank does not exist!')
                        sleep(3)
                        continue
                    if active == passive:
                        print('Tanks cannot shoots at themselves')
                        sleep(3)
                        continue
                    if not passive_tank.alive:
                        print('Tank is already destroyed!')
                        sleep(3)
                        continue
                else:
                    print('Wrong input!')
                    sleep(3)
                    continue

            elif len(active) == 2:
                # input = 1s     1 to shop
                if active[0] in tanks.keys() and active[1] == 's':
                    if not tanks[active[0]].alive:
                        print('Tank is already destroyed!')
                        sleep(1)
                        print('Choose again')
                        continue
                    else:
                        active_tank = tanks[active[0]]
                        shop(active_tank)
                        sleep(2)
                        continue

                # input = 12     1 shoots 2
                if active[0] in tanks.keys() and active[1] in tanks.keys():
                    if not tanks[active[0]].alive or not tanks[active[1]].alive:
                        print('One of these tanks is already destroyed!')
                        sleep(1)
                        print('Choose again')
                        sleep(2)
                        continue
                    if active[0] == active[1]:
                        print('Tanks cannot shoots at themselves')
                        sleep(2)
                        continue
                    else:
                        active_tank = tanks[active[0]]
                        passive_tank = tanks[active[1]]
                else:
                    print('One of these tanks does not exist!')
                    sleep(1)
                    print('Choose again')
                    sleep(2)
                    continue

            # elif len(active) == 3:
            #     # input = 1e3    1 shoots 3
            #     if active[0] in tanks.keys() and active[1].lower() == 'e' and active[2] in tanks.keys():
            #         if not tanks[active[0]].alive or not tanks[active[2]].alive:
            #             print('One of these tanks is already destroyed!')
            #             sleep(1)
            #             print('Choose again')
            #             sleep(2)
            #             continue
            #         if active[0] == active[2]:
            #             print('Tanks cannot shoots at themselves')
            #             sleep(2)
            #             continue
            #         else:
            #             active_tank = tanks[active[0]]
            #             passive_tank = tanks[active[2]]
            #     else:
            #         print('Wrong input!')
            #         sleep(3)
            #         continue
            else:
                print('Wrong input!')
                sleep(3)
                continue
        else:
            print('Wrong input!')
            sleep(3)
            continue

        # get active and passive tanks #
        ############# END ##############

        shot = shoot(active_tank, passive_tank)
        # Tank has a malfunction
        if shot == 'malfunction':
            sleep(2)
            continue
        # Tank missed the enemy
        elif shot == 'miss':
            sleep(1)
            continue
        # Tank hits
        else:
            active_tank.fire_at(passive_tank)

    elif pvc:
        # It's player's turn
        if playersturn:
            print(f"\nIt's {player_tank.name}'s turn")
            sleep(0.5)
            action = input('\nShoot the [E]nemy or go to the [S]hop?  ')
            if action.lower() == 'e':
                print('You shoot...')
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
                playersturn = not playersturn
                continue
            else:
                print('Unknown input!')
                sleep(3)
                continue
        # It's computer's turn
        else:
            print("\nIt's computer's turn\n")
            sleep(1)
            shot = shoot(computer_tank, player_tank)
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
                computer_tank.fire_at(player_tank)

        # print(f'playersturn: {playersturn}')
        playersturn = not playersturn
        # print(f'playersturn: {playersturn}')
        # input('weiter...')
    else:
        print('ERROR')
        print('this should never occure')

    # number of alive tanks minus 1 => last one is the winner
    alive_tanks = get_alive_tanks() - 1
    sleep(2)

for tank in tanks.values():
    if tank.alive:
        print()
        print(f'{tank.name} is the winner - WOOHOO')
        print()

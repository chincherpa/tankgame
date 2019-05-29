import random
import sys
from time import sleep
from colorclass import Color

SETTINGS = {
    'probability_to_miss': 20,
    'probability_of_malfunction': 5,
    'credits': 0,
}

DEBUG = True


def print_slow(str):
    for letter in str:
        # print(letter, end='')
        sleep(.05)


def spinning_cursor(duration, value=None):
    for _ in range(duration):
        for cursor in '|/-\\':
            sleep(0.1)
            sys.stdout.write(f'\r{cursor} {value}')
            sys.stdout.flush()


class Tank:
    """
    Creates a tank
    *Parameters*
    - name              : Name of the tank/player
    - armor             : amount of armor, -damage when hit
    - ammo              : amount of shells, -1 per shot
    - power             : damage per shell
    - alive             : is tank alive?, starts with TRUE
    - ARMORSTART        : armor at the beginning, to calculate percent
    - dmg_mitigation    : Mitigation of incoming damage, -1 per hit
######    - size              : tanks have a size/weight (heavy = strong, more dmg_mitigation -> low ammo, "slow")
    
    - miss              : tanks can miss, initvalue in settings
    - malfunction       : tanks can have a malfunction, initvalue in settings
    - credits           : amount of credits, +1 per hit, initvalue in settings

    + dodge             :
    
    """

    def __init__(self, name, armor, ammo, power, dmg_mitigation):
        self.name = name
        self.armor = armor
        self.ammo = ammo
        self.power = power
        self.dmg_mitigation = dmg_mitigation
        self.miss = SETTINGS['probability_to_miss']
        self.malfunction = SETTINGS['probability_of_malfunction']
        self.credits = SETTINGS['credits']
        self.alive = True
        self.ARMORSTART = armor
        self.shots = 0
        self.hits = 0
        self.misses = 0
        self.malfuncs = 0
        self.dmg = 0

    def __str__(self):
        if self.alive:
            armor = int((self.armor / self.ARMORSTART) * 100)
            return f'{self.name} has {armor}% armor and {self.ammo} shells ({self.power} power) left.'\
                   f'\n{self.name} can mitigate {self.dmg_mitigation}% of damage.'\
                   f'\n- Chance to miss:   {self.miss}%.'\
                   f'\n- Chance to malfunc: {self.malfunction}%.'
        else:
            return f'{self.name} is already destroyed!'

    def fire_at(self, target):
        self.shots += 1
        # Check if tank hits
        treffer = random.randint(1, 101)
        # print('')
        if not DEBUG: print_slow('/' + chr(172) * 20 + '\\')
        if treffer <= self.miss:
            self.misses += 1
            # print('\n')
            # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * 20))
            # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * 8),
                  # Color('{bgmagenta}{white}MISS{/white}{/bgmagenta}'),
                  # Color('{bgmagenta}{white} {/white}{/bgmagenta}' * 8), sep='')
            # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * 20))
            if not DEBUG: sleep(1)
        else:
            self.ammo -= 1
            self.credits += 1
            # sleep(2)
            target.hit(self.power)

    def hit(self, power):
        self.hits += 1
        # armor is decreased by (power of shell - dmg mitigation)
        damage = int(power * float((100 - self.dmg_mitigation)/100))
        self.dmg += damage
        self.armor -= damage
        if self.armor < 0:
            self.armor = 0
        
        # dmg mitigation is decreased by 1
        self.dmg_mitigation -= 1
        if self.dmg_mitigation < 0:
            self.dmg_mitigation = 0

        # probability of malfunction is increased by 1
        self.malfunction += 1

        # calculate x = number of '#' before and after
        x = int((70 - len('BOOM! - %s is hit!' % (self.name))) / 2)
        y = int((70 - len('and looses %i armor!' % (damage))) / 2)
        # print('\n')
        # print(Color('{autobgred}{autowhite} {/white}{/bgred}' * 70))
        # print(Color('{autobgred}{autowhite} {/white}{/bgred}' * x),
              # Color('{autobgred}{autowhite}BOOM! - %s is hit!{/white}{/bgred}' % (self.name)),
              # Color('{autobgred}{autowhite} {/white}{/bgred}') * x, sep='')
        # print(Color('{autobgred}{autowhite} {/white}{/bgred}' * y),
              # Color('{autobgred}{autowhite}and looses %i armor!{/white}{/bgred}' % (damage)),
              # Color('{autobgred}{autowhite} {/white}{/bgred}') * y, sep='')
        # print(Color('{autobgred}{autowhite} {/white}{/bgred}' * 70))
        if self.armor == 0:
            self.explode()

    def explode(self):
        if not DEBUG: sleep(2)
        # tank is destroyed
        self.alive = False
        x = int((70 - len('KAWOOM! - %s explodes!' % (self.name))) / 2)
        y = int((70 - len('KAWOOM! - %s is destroyed!' % (self.name))) / 2)
        # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * 70))
        # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * x),
              # Color('{bgmagenta}{white}KAWOOM! - %s explodes!{/white}{/bgmagenta}' % (self.name)),
              # Color('{bgmagenta}{white} {/white}{/bgmagenta}') * x, sep='')
        # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * 70))
        if not DEBUG: sleep(1)
        # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * y),
              # Color('{bgmagenta}{white}KAWOOM! - %s is destroyed!{/white}{/bgmagenta}' % (self.name)),
              # Color('{bgmagenta}{white} {/white}{/bgmagenta}') * y, sep='')
        # print(Color('{bgmagenta}{white} {/white}{/bgmagenta}' * 70))

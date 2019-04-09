import random
import sys
from time import sleep
from colorclass import Color

SETTINGS = {
    'probability_to_miss': 20,
    'probability_of_malfunction': 5,
    'credits': 5,
}


def print_slow(str):
    for letter in str:
        print(letter, end='')
        sleep(.1)


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
        # Check if tank hits
        treffer = random.randint(1, 101)
        print('')
        # spinning_cursor(3, 'The projectile flies...')
        # print('The projectile flies...\n')
        print_slow('/' + chr(172) * 20 + '\\')
        if treffer <= self.miss:
            print('\n')
            print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 20))
            print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 7),
                  Color('{bgmagenta}{white}MISS{/white}{/bgmagenta}'),
                  Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 7))
            print(Color('{bgmagenta}{white}X{/white}{/bgmagenta}' * 20))
            sleep(2)
        else:
            self.ammo -= 1
            self.credits += 1
            # sleep(2)
            target.hit(self.power)

    def hit(self, power):
        # armor is decreased by (power of shell - dmg mitigation)
        damage = int(power * float((100 - self.dmg_mitigation)/100))
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
        x = int((70 - len('BOOM! - %s is hit!' % (self.name)) - 2) / 2)
        y = int((70 - len('and looses %i armor!' % (damage)) - 2) / 2)
        print('\n')
        print(Color('{autobgred}{autowhite}#{/white}{/bgred}' * 70))
        print(Color('{autobgred}{autowhite}#{/white}{/bgred}' * x),
              Color('{autobgred}{autowhite}BOOM! - %s is hit!{/white}{/bgred}' % (self.name)),
              Color('{autobgred}{autowhite}#{/white}{/bgred}') * x)
        print(Color('{autobgred}{autowhite}#{/white}{/bgred}' * y),
              Color('{autobgred}{autowhite}and looses %i armor!{/white}{/bgred}' % (damage)),
              Color('{autobgred}{autowhite}#{/white}{/bgred}') * y)
        print(Color('{autobgred}{autowhite}#{/white}{/bgred}' * 70))
        if self.armor == 0:
            self.explode()

    def explode(self):
        sleep(2)
        # tank is destroyed
        self.alive = False
        x = int((70 - len('KAWOOM! - %s explodes!' % (self.name)) - 2) / 2)
        y = int((70 - len('KAWOOM! - %s is destroyed!' % (self.name)) - 2) / 2)
        print(Color('{bgmagenta}{white}#{/white}{/bgmagenta}' * 70))
        print(Color('{bgmagenta}{white}#{/white}{/bgmagenta}' * x),
              Color('{bgmagenta}{white}KAWOOM! - %s explodes!{/white}{/bgmagenta}' % (self.name)),
              Color('{bgmagenta}{white}#{/white}{/bgmagenta}') * x)
        print(Color('{bgmagenta}{white}#{/white}{/bgmagenta}' * 70))
        sleep(1)
        print(Color('{bgmagenta}{white}#{/white}{/bgmagenta}' * y),
              Color('{bgmagenta}{white}KAWOOM! - %s is destroyed!{/white}{/bgmagenta}' % (self.name)),
              Color('{bgmagenta}{white}#{/white}{/bgmagenta}') * y)
        print(Color('{bgmagenta}{white}#{/white}{/bgmagenta}' * 70))

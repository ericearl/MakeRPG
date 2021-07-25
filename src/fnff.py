import argparse
import math
import random
import re
from cli2gui import Cli2Gui

def roll(dice_str):
    search = re.match(r'([0-9]+)d([0-9]+)\ *(\+|-)*\ *(stat|[0-9]*)', dice_str)
    if search.group(1) == None and search.group(2) == None:
        print('ERROR: Invalid dice (' + dice_str + ')')

    quantity = int(search.group(1))
    sides = int(search.group(2))
    if search.group(3) == None or search.group(4) == 'stat':
        offset = 0
    else:
        offset = int(search.group(3)+search.group(4))

    total = 0
    for die in range(quantity):
        total += random.choice(range(sides)) + 1

    return total + offset

def locate():
    location = roll('1d10')
    if location == 1:
        return 'Head'
    elif location >= 2 and location <= 4:
        return 'Torso'
    elif location == 5:
        return 'Right Arm'
    elif location == 6:
        return 'Left Arm'
    elif location == 7 or location == 8:
        return 'Right Leg'
    elif location == 9 or location == 10:
        return 'Left Leg'

def semiauto_fumble():
    d10 = roll('1d10')
    if d10 >= 1 and d10 <= 4:
        return 'No fumble.  You just screw up.'
    elif d10 == 5:
        return 'You drop your weapon.'
    elif d10 == 6:
        return 'Weapon discharges (make reliability roll for non-autoweapon) or strikes something harmless.'
    elif d10 == 7:
        return 'Weapon jams (make reliability roll for non-autoweapon) or embeds itself in the ground for one round.'
    elif d10 == 8:
        return 'You manage to wound yourself in the ' + locate() + '.'
    elif d10 >= 9 and d10 <= 10:
        return 'You manage to wound a member of your own party.'

def prop_armor(sp1, sp2):
    sp_base = max([sp1, sp2])
    sp_diff = abs(sp1 - sp2)
    if sp_diff >= 0 and sp_diff <= 4:
        return sp_base + 5
    elif sp_diff >= 5 and sp_diff <= 8:
        return sp_base + 4
    elif sp_diff >= 9 and sp_diff <= 14:
        return sp_base + 3
    elif sp_diff >= 15 and sp_diff <= 20:
        return sp_base + 2
    elif sp_diff >= 21 and sp_diff <= 26:
        return sp_base + 1
    elif sp_diff >= 27:
        return sp_base + 0

def btm_lookup(body):
    if body >= 1 and body <= 2:
        return 0
    elif body >= 3 and body <= 4:
        return 1
    elif body >= 5 and body <= 7:
        return 2
    elif body >= 8 and body <= 9:
        return 3
    elif body == 10:
        return 4
    elif body > 10:
        return 5

def semiauto(args):
    # character stuff
    atk_stat_skill_base = args.a_base
    # dfd_sp_armor = args.d_armor
    # dfd_body = args.d_body

    # weapon stuff
    weapon_damage = args.w_damage
    shots = args.w_shots
    # ap_rounds = args.w_ap

    # referee stuff
    dv = args.r_dv
    # sp_cover = args.r_cover

    # btm = btm_lookup(dfd_body)
    d10_roll = roll('1d10')
    hit = d10_roll

    if hit == 1:
        f_message = semiauto_fumble()
        print( 'Semi-Auto: FUMBLE.  ' + f_message )
        return

    while d10_roll == 10:
        d10_roll = roll('1d10')
        hit += d10_roll

    hit += atk_stat_skill_base
    if hit >= dv:
        for i in range(shots):
            base_damage = roll(weapon_damage)
            location = locate()

            # if sp_cover > 0:
            #     sp = max([sp_cover, dfd_sp_armor]) + sp_bonus(sp_cover, dfd_sp_armor)
            # else:
            #     sp = dfd_sp_armor

            # if ap_rounds:
            #     sp = sp / 2
            #     damage = (base_damage / 2)
            # else:
            #     damage = base_damage

            # if location == 'Head':
            #     final_damage = (damage * 2) - btm
            # else:
            #     final_damage = damage - btm

            print( 'Shot ' + str(i+1) + ': SUCCESS with To Hit = ' + str(hit) + ' versus DV = ' + str(dv) + ' at ' + location + ' for [' + str(base_damage) + ' base damage (before any AP rounds, armor, cover, location, and BTM)]' )
    else:
        print( 'FAILURE with To Hit = ' + str(hit) + ' versus DV = ' + str(dv) )

def auto(args):
    # character stuff
    atk_stat_skill_base = args.a_base
    # dfd_sp_armor = args.d_armor
    # dfd_body = args.d_body

    # weapon stuff
    shots_fired = args.w_shots
    weapon_damage = args.w_damage
    # ap_rounds = args.w_ap

    # referee stuff
    dv = args.r_dv
    # sp_cover = args.r_cover

    # btm = btm_lookup(dfd_body)
    d10_roll = roll('1d10')
    hit = d10_roll

    if hit == 1:
        print( 'Full Auto: FUMBLE.  Roll on Reliability Table, page 106.' )
        return

    while d10_roll == 10:
        d10_roll = roll('1d10')
        hit += d10_roll

    hit += atk_stat_skill_base
    if hit > dv:
        shots_hit = min([hit - dv, shots_fired])
        for i in range(shots_hit):
            base_damage = roll(weapon_damage)
            location = locate()

            # if sp_cover > 0:
            #     sp = max([sp_cover, dfd_sp_armor]) + sp_bonus(sp_cover, dfd_sp_armor)
            # else:
            #     sp = dfd_sp_armor

            # if ap_rounds:
            #     sp = sp / 2
            #     damage = (base_damage / 2)
            # else:
            #     damage = base_damage

            # if location == 'Head':
            #     final_damage = (damage * 2) - btm
            # else:
            #     final_damage = damage - btm

            print( 'Full Auto (Bullet ' + str(i+1) + '): SUCCESS with To Hit = ' + str(hit) + ' versus DV = ' + str(dv) + ' at ' + location + ' for [' + str(base_damage) + ' base damage (before any AP rounds, armor, cover, location, and BTM)]' )
    else:
        print( 'Full Auto: FAILURE with To Hit = ' + str(hit) + ' versus DV = ' + str(dv) )

def suppress(args):
    pass

def burst(args):
    # character stuff
    atk_stat_skill_base = args.a_base
    # dfd_sp_armor = args.d_armor
    # dfd_body = args.d_body

    # weapon stuff
    weapon_damage = args.w_damage
    # ap_rounds = args.w_ap

    # referee stuff
    dv = args.r_dv
    # sp_cover = args.r_cover

    # btm = btm_lookup(dfd_body)
    d10_roll = roll('1d10')
    hit = d10_roll

    if hit == 1:
        print( '3-Round Burst: FUMBLE.  Roll on Reliability Table, page 106.' )
        return

    while d10_roll == 10:
        d10_roll = roll('1d10')
        hit += d10_roll

    hit += atk_stat_skill_base
    if hit >= dv:
        for i in range(roll('1d3')):
            base_damage = roll(weapon_damage)
            location = locate()

            # if sp_cover > 0:
            #     sp = max([sp_cover, dfd_sp_armor]) + sp_bonus(sp_cover, dfd_sp_armor)
            # else:
            #     sp = dfd_sp_armor

            # if ap_rounds:
            #     sp = sp / 2
            #     damage = (base_damage / 2)
            # else:
            #     damage = base_damage

            # if location == 'Head':
            #     final_damage = (damage * 2) - btm
            # else:
            #     final_damage = damage - btm

            # print( '3-Round Burst (Bullet ' + str(i+1) + '): SUCCESS with To Hit = ' + str(hit) + ' versus DV = ' + str(dv) + ' at ' + location + ' against ' + str(sp) + ' SP for [' + str(final_damage) + ' damage]' )
            print( '3-Round Burst (Bullet ' + str(i+1) + '): SUCCESS with To Hit = ' + str(hit) + ' versus DV = ' + str(dv) + ' at ' + location + ' for [' + str(base_damage) + ' base damage (before any AP rounds, armor, cover, location, and BTM)]' )
    else:
        print( '3-Round Burst: FAILURE with To Hit = ' + str(hit) + ' versus DV = ' + str(dv) )

def damage(args):
    # character stuff
    armors = args.armor + args.cover
    btm = btm_lookup(args.body)

    # damage stuff
    ap_rounds = args.ap
    headshot = args.headshot

    # referee stuff
    base_damage = args.base_damage

    # validate arguments

    # layered armor & cover
    if len(armors) == 0:
        sp = 0
    else:
        inner = armors[0]
        for i in range(1, len(armors)):
            if armors[i] == 0:
                continue
            outer = armors[i]
            inner = prop_armor(inner, outer)

        sp = inner

    # armor piercing rounds
    if ap_rounds:
        post_sp = math.floor(sp / 2)
        post_damage = math.floor((base_damage - post_sp) / 2)
        ap_str = ' with AP rounds'
    else:
        post_damage = base_damage - sp
        ap_str = ''

    # location == 'Head' means a headshot
    if headshot:
        post_damage = post_damage * 2
        headshot_str = ' Headshot'
    else:
        headshot_str = ''

    final_damage = post_damage - btm

    if final_damage < 1:
        final_damage = 1

    if post_damage > 0:
        print('DAMAGE taken after Armor & Cover (' + str(sp) + ' SP) and BTM (' + str(btm) + ')' + headshot_str + ap_str + ': [' + str(final_damage) + ' damage]')
    else:
        print('NO DAMAGE taken because Armor & Cover (' + str(sp) + ' SP) was stronger than the base (' + str(base_damage) + '): [0 damage]')

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers()

p_semiauto = subparser.add_parser('semiauto')
p_semiauto.add_argument('-dv','--ref-dv', type=int, metavar='DV', dest='r_dv', required=True)
p_semiauto.add_argument('-b','--atk-base', type=int, metavar='BASE', dest='a_base', required=True)
p_semiauto.add_argument('-dmg','--wpn-damage', type=str, metavar='DAMAGE', dest='w_damage')
p_semiauto.add_argument('-sh','--wpn-shots', type=int, metavar='SHOTS', dest='w_shots')
p_semiauto.set_defaults(func=semiauto)

p_auto = subparser.add_parser('auto')
p_auto.add_argument('-dv','--ref-dv', type=int, metavar='DV', dest='r_dv', required=True)
p_auto.add_argument('-b','--atk-base', type=int, metavar='BASE', dest='a_base', required=True)
p_auto.add_argument('-dmg','--wpn-damage', type=str, metavar='DAMAGE', dest='w_damage')
p_auto.add_argument('-sh','--wpn-shots', type=int, metavar='SHOTS', dest='w_shots')
p_auto.set_defaults(func=auto)

p_suppress = subparser.add_parser('suppress')
p_suppress.add_argument('','', type=, metavar=, dest=, required=)
p_suppress.set_defaults(func=suppress)

p_burst = subparser.add_parser('burst')
p_burst.add_argument('-dv','--ref-dv', type=int, metavar='DV', dest='r_dv', required=True)
p_burst.add_argument('-b','--atk-base', type=int, metavar='BASE', dest='a_base', required=True)
p_burst.add_argument('-dmg','--wpn-damage', type=str, metavar='DAMAGE', dest='w_damage')
p_burst.set_defaults(func=burst)

p_damage = subparser.add_parser('damage')
p_damage.add_argument('-d','--damage-base', type=int, metavar='DAMAGE', dest='base_damage', required=True)
p_damage.add_argument('-b','--body', type=int, metavar='BODY', dest='body', required=True)
p_damage.add_argument('-arm','--armor', type=int, metavar='SP', dest='armor', nargs='+', default=[],
                        help='Space-separated SP list of armors, from inner to outer layer.  Skip this option if no armor.')
p_damage.add_argument('-ap','--ap-rounds', action='store_true', default=False, dest='ap')
p_damage.add_argument('-hd','--headshot', action='store_true', default=False, dest='headshot')
p_damage.add_argument('-c','--cover', type=int, metavar='SP', dest='cover', nargs=1, default=[],
                        help='SP of cover.  Skip this option if no cover.')
p_damage.set_defaults(func=damage)

args = parser.parse_args()

args.func(args)


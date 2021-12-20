import argparse
import math
import random
import re
from gooey import Gooey

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

def dv(args):
    DV = 0

    if args.target_moving == 'REF 11-12':
        DV += -3
    elif args.target_moving == 'REF 13-14':
        DV += -4
    elif args.target_moving == 'REF>15':
        DV += -5

    DV += args.target_immobile
    DV += args.shooter_fastdraw
    DV += args.ambush
    DV += args.called_shot
    DV += args.ricochet
    DV += args.blinded
    DV += args.target_silhouetted
    DV += args.shooter_turning
    DV += args.akimbo
    DV += args.shooter_moving
    DV += args.hipfire
    DV += args.turret
    DV += args.vehicle_mounted
    DV += args.target_large
    DV += args.target_small
    DV += args.target_tiny
    DV += args.weapon_laser
    DV += args.telescopic_extreme
    DV += args.telescopic_far
    DV += args.targeting_scope
    DV += args.smartgun
    DV += args.smartgoggles
    DV += args.burst_short_range

    if args.full_auto_close:
        DV += int(math.floor( float(args.full_auto_close)/10.0 ))
    if args.full_auto_far:
        DV -= int(math.floor( float(args.full_auto_far)/10.0 ))

    if args.distance <= 1:
        DV += 10
        print('DV (Point Blank): ' + str(DV))
    elif float(args.distance) <= float(args.range)/4.0:
        DV += 15
        print('DV (Close Range): ' + str(DV))
    elif float(args.distance) <= float(args.range)/2.0:
        DV += 20
        print('DV (Medium Range): ' + str(DV))
    elif float(args.distance) <= float(args.range):
        DV += 25
        print('DV (Long Range): ' + str(DV))
    elif float(args.distance) <= float(args.range)*2.0:
        DV += 30
        print('DV (Extreme Range): ' + str(DV))
    else:
        DV += 40
        print('DV (Beyond Extreme Range): ' + str(DV))

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
    for i in range(shots):
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

@Gooey
def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    p_dv = subparser.add_parser('dv')
    p_dv.add_argument('-d','--distance', type=int, metavar='DISTANCE', dest='distance', required=True,
                      help='Distance to target in meters.')
    p_dv.add_argument('-r','--range', type=int, metavar='RANGE', dest='range', required=True,
                      help='Long range of weapon in meters.')
    p_dv.add_argument('-immobile','--target-immobile', action='store_const', const=4, default=0, dest='target_immobile',
                      help='Target immobile')
    p_dv.add_argument('-tm','--target-moving', choices=['REF 11-12','REF 13-14','REF>15'], default=None, dest='target_moving',
                      help='Moving Target REF > 10')
    p_dv.add_argument('-fastdraw','-snapshot','--shooter-fastdraw','--shooter-snapshot', action='store_const', const=-3, default=0, dest='shooter_fastdraw',
                      help='Fast draw/Snapshot')
    p_dv.add_argument('-ambush','--shooter-ambush', action='store_const', const=5, default=0, dest='ambush',
                      help='Ambush')
    p_dv.add_argument('-call','--shooter-called-shot', action='store_const', const=-4, default=0, dest='called_shot',
                      help='Aimed/called shot at body location')
    p_dv.add_argument('-ricochet','--shooter-ricochet', action='store_const', const=-5, default=0, dest='ricochet',
                      help='Ricochet or indirect fire')
    p_dv.add_argument('-blind','--shooter-blinded', action='store_const', const=-3, default=0, dest='blinded',
                      help='Blinded by light or dust')
    p_dv.add_argument('-silhouette','--target-silhouetted', action='store_const', const=2, default=0, dest='target_silhouetted',
                      help='Target Silhouetted')
    p_dv.add_argument('-turning','--shooter-turning', action='store_const', const=-2, default=0, dest='shooter_turning',
                      help='Turning to face target')
    p_dv.add_argument('-akimbo','--weapons-akimbo', action='store_const', const=-3, default=0, dest='akimbo',
                      help='Using two weapons')
    p_dv.add_argument('-sm','--shooter-moving', action='store_const', const=-3, default=0, dest='shooter_moving',
                      help='Firing while running')
    p_dv.add_argument('-hip','--shooter-hipfire', action='store_const', const=-2, default=0, dest='hipfire',
                      help='Firing shoulder arm from hip')
    p_dv.add_argument('-turret','--turret-mounted', action='store_const', const=2, default=0, dest='turret',
                      help='Turret mounted weapon')
    p_dv.add_argument('-vm','--vehicle-mounted', action='store_const', const=-4, default=0, dest='vehicle_mounted',
                      help='Vehicle mounted, no turret')
    p_dv.add_argument('-large','--target-large', action='store_const', const=4, default=0, dest='target_large',
                      help='Large target')
    p_dv.add_argument('-small','--small-target', action='store_const', const=-4, default=0, dest='target_small',
                      help='Small target')
    p_dv.add_argument('-tiny','--target-tiny', action='store_const', const=-6, default=0, dest='target_tiny',
                      help='Tiny target')
    p_dv.add_argument('-aim','--aiming-rounds', type=int, choices=[0,1,2,3], default=0, dest='aiming',
                      help='Aiming combat rounds (+1 each round, up to 3 rounds)')
    p_dv.add_argument('-laser','--weapon-laser', action='store_const', const=1, default=0, dest='weapon_laser',
                      help='Laser sight')
    p_dv.add_argument('-textreme','--telescopic-extreme', action='store_const', const=2, default=0, dest='telescopic_extreme',
                      help='Telescopic sight (Extreme range)')
    p_dv.add_argument('-tfar','--telescopic-far', action='store_const', const=1, default=0, dest='telescopic_far',
                      help='Telescopic sight (Medium or Long range)')
    p_dv.add_argument('-scope','--targeting-scope', action='store_const', const=1, default=0, dest='targeting_scope',
                      help='Targeting scope')
    p_dv.add_argument('-sg','--smartgun', action='store_const', const=2, default=0, dest='smartgun',
                      help='Smartgun')
    p_dv.add_argument('-goggles','--smartgoggles', action='store_const', const=2, default=0, dest='smartgoggles',
                      help='Smartgoggles')
    p_dv.add_argument('-trb','--burst-short-range', action='store_const', const=3, default=0, dest='burst_short_range',
                      help='Three round burst (Close/Medium range only)')
    p_dv.add_argument('-fac','--full-auto-close', type=int, default=0, dest='full_auto_close',
                      help='Full auto, Close (number of rounds fired)')
    p_dv.add_argument('-faf','--full-auto-far', type=int, default=0, dest='full_auto_far',
                      help='Full auto, not Close (number of rounds fired)')
    p_dv.set_defaults(func=dv)

    p_semiauto = subparser.add_parser('semiauto')
    p_semiauto.add_argument('-dv','--ref-dv', type=int, metavar='DV', dest='r_dv', required=True,
                            help='Difficulty Value (DV) To Hit.')
    p_semiauto.add_argument('-b','--atk-base', type=int, metavar='BASE', dest='a_base', required=True,
                            help='Stat + Skill + Weapon Accuracy (WA) in the weapon being used.')
    p_semiauto.add_argument('-dmg','--wpn-damage', type=str, metavar='DAMAGE', dest='w_damage',
                            help='Damage Dice in weapon being used.')
    p_semiauto.add_argument('-sh','--wpn-shots', type=int, metavar='SHOTS', dest='w_shots',
                            help='Number of semi-auto shots being fired.')
    p_semiauto.set_defaults(func=semiauto)

    p_auto = subparser.add_parser('auto')
    p_auto.add_argument('-dv','--ref-dv', type=int, metavar='DV', dest='r_dv', required=True,
                        help='Difficulty Value (DV) To Hit.')
    p_auto.add_argument('-b','--atk-base', type=int, metavar='BASE', dest='a_base', required=True,
                        help='Stat + Skill + Weapon Accuracy (WA) in the weapon being used.')
    p_auto.add_argument('-dmg','--wpn-damage', type=str, metavar='DAMAGE', dest='w_damage',
                        help='Damage Dice in weapon being used.')
    p_auto.add_argument('-sh','--wpn-shots', type=int, metavar='SHOTS', dest='w_shots',
                        help='Rate-of-fire of weapong or remainder of clip being fired.')
    p_auto.set_defaults(func=auto)

    # p_suppress = subparser.add_parser('suppress')
    # p_suppress.add_argument('','', type=, metavar=, dest=, required=)
    # p_suppress.set_defaults(func=suppress)

    p_burst = subparser.add_parser('burst')
    p_burst.add_argument('-dv','--ref-dv', type=int, metavar='DV', dest='r_dv', required=True,
                         help='Difficulty Value (DV) To Hit.')
    p_burst.add_argument('-b','--atk-base', type=int, metavar='BASE', dest='a_base', required=True,
                         help='REF Stat + Weapon Skill + Weapon Accuracy (WA) in the weapon being used.')
    p_burst.add_argument('-dmg','--wpn-damage', type=str, metavar='DAMAGE', dest='w_damage',
                         help='Damage Dice in weapon being used.')
    p_burst.set_defaults(func=burst)

    p_damage = subparser.add_parser('damage')
    p_damage.add_argument('-d','--damage-base', type=int, metavar='DAMAGE', dest='base_damage', required=True,
                          help='Base damage provided by attacking weapon bullet.')
    p_damage.add_argument('-b','--body', type=int, metavar='BODY', dest='body', required=True,
                          help='BODY Stat of character receiving damage.')
    p_damage.add_argument('-arm','--armor', type=int, metavar='ARMOR_SP', dest='armor', nargs='+', default=[],
                          help='Space-separated SP list of armors, from inner to outer layer.  Skip this option if no armor.')
    p_damage.add_argument('-ap','--ap-rounds', action='store_true', default=False, dest='ap',
                          help='Flag for Armor Piercing (AP) round.')
    p_damage.add_argument('-hd','--headshot', action='store_true', default=False, dest='headshot',
                          help='Flag for damage to the head.')
    p_damage.add_argument('-c','--cover', type=int, metavar='COVER_SP', dest='cover', nargs=1, default=[],
                          help='SP of cover.  Skip this option if no cover.')
    p_damage.set_defaults(func=damage)

    args = parser.parse_args()

    args.func(args)

    # TO HIT (DV): Weapon Range vs Distance to target + Cyberware Modifiers + WA + Difficulty Modifiers
    # DAMAGE: Location ( + AP Rounds ) vs Armor SP & Cover SP & soaked up by SDP

main()

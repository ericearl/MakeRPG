import django
import os
import queue
import random
import re
import time
import yaml

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *
from src.spend import *
from modify import *

def parse_dice(dice_str):
    search = re.match(r'([0-9]+)d([0-9]+)\ *(\+|-)*\ *(stat|[0-9]*)', dice_str)
    if search.group(1) == None and search.group(2) == None:
        print('ERROR: Invalid dice (' + dice_str + ') for dice_str ' + dice_str)

    quantity = int(search.group(1))
    sides = int(search.group(2))
    if search.group(3) == None or search.group(4) == 'stat':
        offset = 0
    else:
        offset = int(search.group(3)+search.group(4))

    dice_min = quantity + offset
    dice_max = quantity * sides + offset
    dice_span = list(range(dice_min, dice_max+1))

    return quantity, sides, offset, dice_span


def setter(dice_str):
    quantity, sides, offset, dice_span = parse_dice(dice_str)
    dice = Dice.objects.filter(quantity=quantity).filter(sides=sides).filter(offset=offset)

    if dice:
        d = dice.get()
    else:
        d = Dice()
        d.string = dice_str
        d.quantity = quantity
        d.sides = sides
        d.offset = offset
        d.save()
    
    return d


def random_name(firstnames,lastnames):
    return ' '.join([
        firstnames[random.randint(0, len(firstnames))] ,
        lastnames[random.randint(0, len(lastnames))]
        ])


def get_history_starts(history_tree):
    if 'START' in history_tree and 'NPC' in history_tree:
        return (history_tree['START'], history_tree['NPC'][0])
    elif 'START' in history_tree and 'NPC' not in history_tree:
        return (history_tree['START'], None)
    else:
        print('History YAML file is missing either START or NPC keywords.')
        return (None, None)


def history_modify(tree, c, histmod_dict):
    # "being_modified" might be 'stats' or 'skills' or 'traits' or 'points', etc.
    for being_modified in histmod_dict:
        mod_dict = histmod_dict[being_modified]

        if type(mod_dict) is not dict:
            if being_modified == 'archetype':
                c.archetype = Archetype.objects.get(name=mod_dict)
                c.save()

            elif being_modified == 'role':
                c.role = Role.objects.get(name=mod_dict)
                c.save()

            continue

        # mod_dict is a dictionary of stats, for instance
        for modifier_key in mod_dict:

            equation = mod_dict[modifier_key]

            if being_modified == 'points':
                cx = CharacterPointpool.objects.filter(character=c).get(pointpool__name=modifier_key)
                cx.total = modify_equation(cx.total, equation)
                cx.current = modify_equation(cx.current, equation)

            elif being_modified == 'stats':
                cx = CharacterStatistic.objects.filter(character=c).get(statistic__name=modifier_key)
                cx.current = modify_equation(cx.current, equation)

            elif being_modified == 'skills':
                cx = CharacterSkill.objects.filter(character=c).get(skill__name=modifier_key)
                cx.current = modify_equation(cx.current, equation)

            elif being_modified == 'traits':
                cx = CharacterTrait.objects.filter(character=c).get(trait__name=modifier_key)
                cx.current = modify_equation(cx.current, equation)

            cx.save()

    return


def make_selection(tree, character, eventroll):
    ename = eventroll.mainevent.name
    eroll = eventroll.roll
    
    roll_dict = tree['history'][ename]['roll']

    for roll in roll_dict:

        if eroll == roll:
            selection_dict = roll_dict[roll]
            break
        
        elif type(roll) is str:
            possible_rolls = []
            if ',' in roll:
                # multiple values
                for partial in roll.split(','):
                    if '-' in partial:
                        # a span of comma-separated values
                        minimum,maximum = (int(number) for number in partial.split('-'))
                        values = list(range(minimum,maximum+1))
                        roll_dict[roll] = values
                        possible_rolls += values
                    else:
                        # a single comma-separated value
                        values = int(partial)
                        roll_dict[roll] = [values]
                        possible_rolls.append(values)
            elif '-' in roll:
                # a span of values
                minimum,maximum = (int(number) for number in roll.split('-'))
                values = list(range(minimum,maximum+1))
                roll_dict[roll] = values
                possible_rolls += values
            
            if eroll in possible_rolls:
                selection_dict = roll_dict[roll]
                break

    history_modify(tree, character, selection_dict)

    return


def character_initialize(tree, c):

    flavors = []
    if 'stats' in tree:
        defstat = tree['defaults']['stats']
        flavors.append('stats')
    if 'skills' in tree:
        defskill = tree['defaults']['skills']
        flavors.append('skills')
    if 'traits' in tree:
        deftrait = tree['defaults']['traits']
        flavors.append('traits')

    for flavor in flavors:
        for kind in tree[flavor].keys():
            definition = tree[flavor][kind]
            kinds = {}

            for key in [
                'set',
                'min',
                'max',
                'direction',
                'cost',
                'purchase',
                'tier',
                'type',
                'role',
                'points',
                'archetype',
                'category',
                'unlocks'
                ]:
                if type(definition) is dict and key in definition:
                    kinds[key] = definition[key]
                elif 'stats' in tree and flavor == 'stats' and key in defstat:
                    kinds[key] = defstat[key]
                elif 'skills' in tree and flavor == 'skills' and key in defskill:
                    kinds[key] = defskill[key]
                elif 'traits' in tree and flavor == 'traits' and key in deftrait:
                    kinds[key] = deftrait[key]

            tree[flavor][kind] = kinds

    # initialize all character stats
    if 'stats' in tree:
        for stat_name in tree['stats'].keys():
            stat_min = int(tree['stats'][stat_name]['min'])
            stat_max = int(tree['stats'][stat_name]['max'])
            stat = Statistic.objects.get(name=stat_name)
            cstat = CharacterStatistic()
            cstat.character = c
            cstat.statistic = stat

            # if type(stat_min) is str:
            #     if stat_min[0] == '-':
            #         pos_minimum, cstat.maximum = (int(number) for number in stat_min[1:].split('-'))
            #         cstat.minimum = pos_minimum * (-1)
            #     else:
            #         cstat.minimum, cstat.maximum = (int(number) for number in stat_range.split('-'))
            # elif type(stat_min) is int:

            cstat.minimum = stat_min
            cstat.maximum = stat_max

            if stat.type == IND:

                stat_set = tree['stats'][stat_name]['set']
                if tree['stats'][stat_name]['points'] == 'roll':

                    if type(stat_set) is str:
                        d = setter(stat_set)
                        if stat.direction == 'increasing':
                            cstat.current = cstat.minimum + d.roll()
                        elif stat.direction == 'decreasing':
                            cstat.current = cstat.maximum - d.roll()

                    elif type(stat_set) is int:
                        cstat.current = stat_set

            elif stat.type == DEP:
                cstat.current = stat_set

            cstat.save()

    # initialize all character skills
    if 'skills' in tree:
        for skill in Skill.objects.all():
            if skill.role.name == 'none' or skill.role.name == c.role.name:
                skill_min = tree['skills'][skill.name]['min']
                skill_max = tree['skills'][skill.name]['max']
                cskill = CharacterSkill()
                cskill.character = c
                cskill.skill = skill

                # if type(skill_range) is str:
                #     if skill_range[0] == '-':
                #         pos_minimum, cskill.maximum = (int(number) for number in skill_range[1:].split('-'))
                #         cskill.minimum = pos_minimum * (-1)
                #     else:
                #         cskill.minimum, cskill.maximum = (int(number) for number in skill_range.split('-'))
                # elif type(skill_range) is int:
                cskill.minimum = skill_min
                cskill.maximum = skill_max

                if skill.direction == 'increasing':
                    cskill.current = cskill.minimum
                elif skill.direction == 'decreasing':
                    cskill.current = cskill.maximum

                cskill.save()

    # initialize all character skills
    if 'traits' in tree:
        for trait in Trait.objects.all():
            trait_min = tree['traits'][trait.name]['min']
            trait_max = tree['traits'][trait.name]['max']
            ctrait = CharacterTrait()
            ctrait.character = c
            ctrait.trait = trait

            # if type(skill_range) is str:
            #     if skill_range[0] == '-':
            #         pos_minimum, cskill.maximum = (int(number) for number in skill_range[1:].split('-'))
            #         cskill.minimum = pos_minimum * (-1)
            #     else:
            #         cskill.minimum, cskill.maximum = (int(number) for number in skill_range.split('-'))
            # elif type(skill_range) is int:
            ctrait.minimum = trait_min
            ctrait.maximum = trait_max

            if trait.direction == 'increasing':
                ctrait.current = ctrait.minimum
            elif trait.direction == 'decreasing':
                ctrait.current = ctrait.maximum

            ctrait.save()

    # initialize all character pointpools
    for p in Pointpool.objects.all():
        if p.name != 'roll':
            cpoints = CharacterPointpool()
            cpoints.character = c
            cpoints.pointpool = p

            points_set = tree['points'][p.name]['set']
            if type(points_set) is int:
                cpoints.current = points_set
                cpoints.total = points_set
            elif type(points_set) is str:
                d = setter(points_set)
                cpoints.current = d.roll()
                cpoints.total = cpoints.current

            cpoints.save()


# roll character history
def history(tree, character):

    history_start, npc_start = get_history_starts(tree['history'])

    current = Event.objects.get(name=history_start)

    next_q = queue.LifoQueue()
    reroll_q = queue.LifoQueue()
    # npc_q = queue.Queue()

    next_q.put(current)

    while not next_q.empty():
        current = next_q.get()
        event_rolls = EventRoll.objects.filter(mainevent=current)

        if not event_rolls:
            continue

        er = random.choice(event_rolls)

        if er.selection:
            make_selection(tree, character, er)

        cer = CharacterEventRoll()
        cer.character = character
        cer.eventroll = er
        cer.save()

        if current.nextevent:
            next_q.put(current.nextevent)

        # if er.npc:
        #     for i in range(er.rerollcount):
        #         npc_q.put(er.npc)

        if er.rollevent and er.rerollcount > 1:
            for i in range(er.rerollcount):
                reroll_q.put(er.rollevent)
        elif er.rollevent:
            next_q.put(er.rollevent)
        elif er.nextevent:
            next_q.put(er.nextevent)

    while not reroll_q.empty():
        current = reroll_q.get()
        event_rolls = EventRoll.objects.filter(mainevent=current)
        er = random.choice(event_rolls)
        cer = CharacterEventRoll()
        cer.character = character
        cer.eventroll = er
        cer.save()

        # if er.npc:
        #     for i in range(er.rerollcount):
        #         npc_q.put(er.npc)

        if er.rollevent:
            reroll_q.put(er.rollevent)
        elif current.nextevent:
            reroll_q.put(current.nextevent)

    # # NEW RULES ARE THAT ROLES AND ARCHETYPES MUST BE PART OF HISTORY ROLLS
    # while not npc_q.empty():
    #     npc = Character()
    #     npc.name = '[NPC ' + npc_q.get() + '] ' + random_name(firstnames, lastnames)
    #     # if len(all_roles) > 0:
    #     #     npc.role = random.choice(all_roles)
    #     npc.save()

    #     # roll(npc, skillstats) # TODO: ALLOW FOR THIS AFTER HISTORY ROLLS

    #     npc_event = Event.objects.get(name=npc_start)
    #     while True:
    #         npc_event_rolls = EventRoll.objects.filter(mainevent=npc_event)
    #         npc_event_roll = random.choice(npc_event_rolls)

    #         npc_er = NPCEventRoll()
    #         npc_er.npc = npc
    #         npc_er.character = character
    #         npc_er.eventroll = npc_event_roll
    #         npc_er.save()

    #         try:
    #             npc_event = NPCEvent.objects.get(current=npc_event).next
    #         except:
    #             break


if __name__ == '__main__':
    # character count to make per run
    character_count = 40
    system_yaml = 'Examples/mothership/system.yaml'

    # needs error handling
    with open(system_yaml, 'r') as yamlfile:
        tree = yaml.load(yamlfile)

    history_tree = tree['history']
    history_start, npc_start = get_history_starts(history_tree)

    # names lists
    with open('MakeRPG/firstnames.txt', 'r') as firsts:
        firstnames = [name.strip('\n') for name in firsts.readlines()]
    with open('MakeRPG/lastnames.txt', 'r') as lasts:
        lastnames = [name.strip('\n') for name in lasts.readlines()]

    tstart = time.time()

    for _ in range(character_count):
        char_tstart = time.time()

        c = Character()
        c.name = random_name(firstnames, lastnames)
        c.save()

        character_initialize(tree, c)

        history(tree, c)

        if 'stats' in tree:
            spend_stats(tree, c)
        if 'skills' in tree:
            spend_skills(tree, c)
        if 'traits' in tree:
            spend_traits(tree, c)

        if 'modifiers' in tree:

            if 'points' in tree['modifiers']:
                modify(c, tree, 'points')

                if 'stats' in tree:
                    spend_stats(tree, c)
                if 'skills' in tree:
                    spend_skills(tree, c)
                if 'traits' in tree:
                    spend_traits(tree, c)

            if 'stats' in tree['modifiers']:
                modify(c, tree, 'stats')
            if 'skills' in tree['modifiers']:
                modify(c, tree, 'skills')
            if 'traits' in tree['modifiers']:
                modify(c, tree, 'traits')


        char_tstop = time.time()
        print('%s made in %0.1f seconds' % (c, char_tstop-char_tstart))

    tstop = time.time()

    elapsed_time = tstop - tstart
    avg_character_time = elapsed_time / character_count
    # avg_character_npc_time = elapsed_time / (character_count + npc_count)

    print('Created %d character(s) in %0.2f minutes' % (character_count, elapsed_time/60))
    print('Average full character time: %0.1f seconds' % (avg_character_time))
    # print('Average time per character or NPC: %0.1f seconds' % (avg_character_npc_time))

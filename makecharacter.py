import django, os, yaml, random, queue, time
from django.db.models import Sum
from setup import parse_dice

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *


def random_name(firstnames,lastnames):
    return ' '.join([ firstnames[random.randint(0, len(firstnames))] , lastnames[random.randint(0, len(lastnames))] ])


def expand_skillstats(tree):
    defstat = tree['defaults']['stats']
    defskill = tree['defaults']['skills']

    for flavor in ['stats','skills']:
        for kind in tree[flavor].keys():
            definition = tree[flavor][kind]
            kinds = {}

            for key in ['range', 'direction', 'cost', 'purchase', 'tier', 'type', 'role', 'points','set']:
                if type(definition) is dict and key in definition:
                    kinds[key] = definition[key]
                elif flavor == 'stats':
                    kinds[key] = defstat[key]
                elif flavor == 'skills':
                    kinds[key] = defskill[key]

            tree[flavor][kind] = kinds

    return tree


def get_history_starts(tree):
    if 'START' in tree and 'NPC' in tree:
        return (tree['START'], tree['NPC'][0])
    elif 'START' in tree and 'NPC' not in tree:
        return (tree['START'], None)
    else:
        print('History YAML file is missing either START or NPC keywords.')
        return



def spend_points(c, tree, initial=False):
    # spend points from character pointpools
    for cp in CharacterPointpool.objects.filter(character=c):
        cstats = CharacterStatistic.objects.filter(character=c).exclude(statistic__type=DEP)
        cskills = CharacterSkill.objects.filter(character=c)

        if initial:
            # subtract minimum points required to initialize stats and skills
            for cstat in cstats:
                if cstat.statistic.pointpool.name == cp.pointpool.name:
                    if cstat.statistic.direction == 'increasing':
                        for i in range(cstat.current):
                            cp.current -= cstat.statistic.cost * ( (i+1) ** cstat.statistic.tier )
                            cp.save()
                    elif cstat.statistic.direction == 'decreasing':
                        for i in range(cstat.statistic.maximum - cstat.current):
                            cp.current -= cstat.statistic.cost * ( (i+1) ** cstat.statistic.tier )
                            cp.save()

            for cskill in cskills:
                if cp.current > 0 and cskill.skill.pointpool.name == cp.pointpool.name and ( cskill.skill.role.name == 'none' or cskill.skill.role.name == c.role.name ):
                    if cskill.skill.direction == 'increasing':
                        for i in range(cskill.current):
                            cp.current -= cskill.skill.cost * ( (i+1) ** cskill.skill.tier )
                            cp.save()
                    elif cskill.skill.direction == 'decreasing':
                        for i in range(cskill.skill.maximum - cskill.current):
                            cp.current -= cskill.skill.cost * ( (i+1) ** cskill.skill.tier )
                            cp.save()

        # roll all character statistics and skills until their sum is "points"
        choosy = []
        if len(cstats) > 0:
            choosy.append('stat')
        if len(cskills) > 0:
            choosy.append('skill')

        while cp.current > 0:
            if len(cstats) > 0:
                cstat = random.choice(cstats)
            if len(cskills) > 0:
                cskill = random.choice(cskills)

            choice = random.choice(choosy)

            if choice == 'stat' and (
                    ( cstat.statistic.pointpool.name == cp.pointpool.name and cstat.statistic.type != 'dependent' ) or
                    (
                    'roles' in tree and
                    'statpoints' in tree['roles'][c.role.name] and
                    tree['roles'][c.role.name]['statpoints'] == cp.pointpool.name and
                    cstat.statistic.name in tree['roles'][c.role.name]['stats']
                    )
                    ):

                if cstat.statistic.direction == 'increasing' and cstat.current < cstat.statistic.maximum:
                    cost = cstat.statistic.cost * ( (cstat.current+1) ** cstat.statistic.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cstat.current += cstat.statistic.purchase.roll()
                        cstat.save()
                        cp.save()
                elif cstat.statistic.direction == 'decreasing' and cstat.current > cstat.statistic.minimum:
                    cost = cstat.statistic.cost * ( (cstat.statistic.maximum - cstat.current + 1) ** cstat.statistic.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cstat.current -= cstat.statistic.purchase.roll()
                        cstat.save()
                        cp.save()

            if choice == 'skill' and (
                    cskill.skill.pointpool.name == cp.pointpool.name or
                    (
                    'roles' in tree and
                    'skillpoints' in tree['roles'][c.role.name] and
                    tree['roles'][c.role.name]['skillpoints'] == cp.pointpool.name and
                    cskill.skill.name in tree['roles'][c.role.name]['skills']
                    )
                    ):

                if cskill.skill.direction == 'increasing' and cskill.current < cskill.skill.maximum:
                    cost = cskill.skill.cost * ( (cskill.current+1) ** cskill.skill.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cskill.current += cskill.skill.purchase.roll()
                        cskill.save()
                        cp.save()
                elif cskill.skill.direction == 'decreasing' and cskill.current > cskill.skill.minimum:
                    cost = cskill.skill.cost * ( (cskill.skill.maximum - cskill.current + 1) ** cskill.skill.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cskill.current -= cskill.skill.purchase.roll()
                        cskill.save()
                        cp.save()


def modify(c, tree, modifier):
    for being_modified in tree['modifiers'][modifier]:
        for modifier_key in tree['modifiers'][modifier][being_modified]:
            for modifier_lookup in tree['modifiers'][modifier][being_modified][modifier_key]:
                if modifier_key == 'stats':
                    cs = CharacterStatistic.objects.filter(character=c).get(statistic__name=modifier_lookup)
                elif modifier_key == 'skills':
                    cs = CharacterSkill.objects.filter(character=c).get(skill__name=modifier_lookup)

                if modifier == 'points':
                    cx = CharacterPointpool.objects.filter(character=c).get(pointpool__name=being_modified)
                elif modifier == 'stats':
                    cx = CharacterStatistic.objects.filter(character=c).get(statistic__name=being_modified)
                elif modifier == 'skills':
                    cx = CharacterSkill.objects.filter(character=c).get(skill__name=being_modified)

                lookup = tree['modifiers'][modifier][being_modified][modifier_key][modifier_lookup]

                possible_rolls = []
                # a dictionary of roll value lists whose keys are roll strings
                roll_dict = {}
                for element in lookup.keys():
                    roll_str = str(element)

                    if '-' not in roll_str and ',' not in roll_str:
                        # a single value
                        values = int(roll_str)
                        roll_dict[roll_str] = [values]
                        possible_rolls.append(values)
                    elif ',' in roll_str:
                        # multiple values
                        for partial in roll_str.split(','):
                            if '-' in partial:
                                # a span of comma-separated values
                                minimum,maximum = (int(number) for number in partial.split('-'))
                                values = list(range(minimum,maximum+1))
                                roll_dict[roll_str] = values
                                possible_rolls += values
                            else:
                                # a single comma-separated value
                                values = int(partial)
                                roll_dict[roll_str] = [values]
                                possible_rolls.append(values)
                    elif '-' in roll_str:
                        # a span of values
                        minimum,maximum = (int(number) for number in roll_str.split('-'))
                        values = list(range(minimum,maximum+1))
                        roll_dict[roll_str] = values
                        possible_rolls += values

                for key in lookup.keys():
                    if cs.current in roll_dict[str(key)]:
                        outcome = lookup[key]
                        cx.current += outcome
                        cx.save()
                        break


def roll(c, tree):
    # initialize all character statistics
    for stat_name in tree['stats'].keys():
        stat_range = tree['stats'][stat_name]['range']
        stat = Statistic.objects.get(name=stat_name)
        cstat = CharacterStatistic()
        cstat.character = c
        cstat.statistic = stat

        if type(stat_range) is str:
            if stat_range[0] == '-':
                pos_minimum, cstat.maximum = (int(number) for number in stat_range[1:].split('-'))
                cstat.minimum = pos_minimum * (-1)
            else:
                cstat.minimum, cstat.maximum = (int(number) for number in stat_range.split('-'))
        elif type(stat_range) is int:
            cstat.minimum = stat_range
            cstat.maximum = stat_range

        if stat.type == IND:
            if tree['stats'][stat_name]['points'] == 'roll':
                quantity, sides, offset, dice_span = parse_dice(tree['stats'][stat_name]['set'])
                cstat.current = random.choice(dice_span)
            if stat.direction == 'increasing':
                cstat.current = stat.minimum
            elif stat.direction == 'decreasing':
                cstat.current = stat.maximum
        elif stat.type == DEP:
            cstat.current = tree['stats'][stat_name]['set']

        cstat.save()

    # initialize all character skills
    for skill in Skill.objects.all():
        if skill.role.name == 'none' or skill.role.name == c.role.name:
            skill_range = tree['skills'][skill.name]['range']
            cskill = CharacterSkill()
            cskill.character = c
            cskill.skill = skill

            if type(skill_range) is str:
                if skill_range[0] == '-':
                    pos_minimum, cskill.maximum = (int(number) for number in skill_range[1:].split('-'))
                    cskill.minimum = pos_minimum * (-1)
                else:
                    cskill.minimum, cskill.maximum = (int(number) for number in skill_range.split('-'))
            elif type(skill_range) is int:
                cskill.minimum = skill_range
                cskill.maximum = skill_range

            if skill.direction == 'increasing':
                cskill.current = skill.minimum
            elif skill.direction == 'decreasing':
                cskill.current = skill.maximum

            cskill.save()

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
                quantity, sides, offset, dice_span = parse_dice(points_set)
                dice = Dice.objects.filter(quantity=quantity).filter(sides=sides).filter(offset=offset)

                if dice:
                    d = dice.get()
                else:
                    d = Dice()
                    d.string = points_set
                    d.quantity = quantity
                    d.sides = sides
                    d.offset = offset
                    d.save()

                cpoints.current = d.roll()
                cpoints.total = cpoints.current

            cpoints.save()

    spend_points(c, tree, initial=True)

    if 'modifiers' in tree:

        if 'points' in tree['modifiers']:
            modify(c, tree, 'points')
            spend_points(c, tree)

        if 'stats' in tree['modifiers']:
            modify(c, tree, 'stats')

        if 'skills' in tree['modifiers']:
            modify(c, tree, 'skills')


if __name__ == '__main__':
    # character count to make per run
    character_count = 3
    system_yaml = 'Examples/cyberpunk_2020/system.yaml'

    # needs error handling
    with open(system_yaml, 'r') as yamlfile:
        tree = yaml.load(yamlfile)

    history = tree['history']
    skillstats = expand_skillstats( tree )

    history_start, npc_start = get_history_starts(history)

    # names lists
    with open('MakeRPG/firstnames.txt', 'r') as firsts:
        firstnames = [name.strip('\n') for name in firsts.readlines()]
    with open('MakeRPG/lastnames.txt', 'r') as lasts:
        lastnames = [name.strip('\n') for name in lasts.readlines()]

    tstart = time.time()
    npc_count = 0
    for _ in range(character_count):
        char_tstart = time.time()

        c = Character()
        c.name = random_name(firstnames, lastnames)
        all_roles = Role.objects.all().exclude(name='none')
        if len(all_roles) > 0:
            c.role = random.choice(all_roles)
        c.save()

        # BIG IMPORTANT DEAL FOR SKILLS AND STATS
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        roll(c, skillstats)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        # roll character history
        current = Event.objects.get(name=history_start)

        next_q = queue.LifoQueue()
        reroll_q = queue.LifoQueue()
        npc_q = queue.Queue()

        next_q.put(current)

        while not next_q.empty():
            current = next_q.get()
            event_rolls = EventRoll.objects.filter(mainevent=current)
            er = random.choice(event_rolls)
            cer = CharacterEventRoll()
            cer.character = c
            cer.eventroll = er
            cer.save()

            ename = er.mainevent.name
            eroll = er.roll

            rolly = history[ename]['roll'][eroll]
            if type(rolly) is dict:
                for key in rolly:
                    if key == 'archetypes':
                        c.archetype = Archetype.objects.filter(name=rolly['archetypes'])
                    elif key == 'points':
                        rolly[key]
                    elif key == 'currency':
                        rolly[key]
                    elif key == 'stats':
                        rolly[key]
                    elif key == 'skills':
                        rolly[key]

            if current.nextevent:
                next_q.put(current.nextevent)

            if er.npc:
                for i in range(er.rerollcount):
                    npc_q.put(er.npc)

            if er.rollevent and er.rerollcount > 1:
                for i in range(er.rerollcount):
                    reroll_q.put(er.rollevent)
            elif er.rollevent:
                next_q.put(er.rollevent)

        while not reroll_q.empty():
            current = reroll_q.get()
            event_rolls = EventRoll.objects.filter(mainevent=current)
            er = random.choice(event_rolls)
            cer = CharacterEventRoll()
            cer.character = c
            cer.eventroll = er
            cer.save()

            if er.npc:
                for i in range(er.rerollcount):
                    npc_q.put(er.npc)

            if er.rollevent:
                reroll_q.put(er.rollevent)
            elif current.nextevent:
                reroll_q.put(current.nextevent)

        while not npc_q.empty():
            npc_tstart = time.time()
            npc_count += 1

            npc = Character()
            npc.name = '[NPC ' + npc_q.get() + '] ' + random_name(firstnames, lastnames)
            if len(all_roles) > 0:
                npc.role = random.choice(all_roles)
            npc.save()

            roll(npc, skillstats)

            npc_event = Event.objects.get(name=npc_start)
            while True:
                npc_event_rolls = EventRoll.objects.filter(mainevent=npc_event)
                npc_event_roll = random.choice(npc_event_rolls)

                npc_er = NPCEventRoll()
                npc_er.npc = npc
                npc_er.character = c
                npc_er.eventroll = npc_event_roll
                npc_er.save()

                try:
                    npc_event = NPCEvent.objects.get(current=npc_event).next
                except:
                    break
            npc_tstop = time.time()
            print('%s made in %0.1f seconds' % (npc, npc_tstop-npc_tstart))

        char_tstop = time.time()
        print('%s made in %0.1f seconds' % (c, char_tstop-char_tstart))

    tstop = time.time()

    elapsed_time = tstop - tstart
    avg_character_time = elapsed_time / character_count
    avg_character_npc_time = elapsed_time / (character_count + npc_count)

    print('Created %d character(s) and %d NPC(s) in %0.2f minutes' % (character_count, npc_count, elapsed_time/60))
    print('Average full character with NPC(s) time: %0.1f seconds' % (avg_character_time))
    print('Average time per character or NPC: %0.1f seconds' % (avg_character_npc_time))

import django, os, yaml, random, queue, time
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *


def random_name(firstnames,lastnames):
    return ' '.join([ firstnames[random.randint(0, len(firstnames))] , lastnames[random.randint(0, len(lastnames))] ])


def get_history_starts(tree):
    if 'START' in tree and 'NPC' in tree:
        history_tree = tree
    else:
        print('History YAML file is missing either START or NPC keywords.')
        return

    return (history_tree['START'], history_tree['NPC'][0])


def roll(c, tree):
    # initialize all character statistics
    for stat in Statistic.objects.all():
        if stat.type != DEP:
            cstat = CharacterStatistic()
            cstat.character = c
            cstat.statistic = stat

            if stat.direction == INC:
                cstat.current = stat.minimum
            elif stat.direction == DEC:
                cstat.current = stat.maximum

            cstat.save()

    # initialize all character skills
    for skill in Skill.objects.all():
        if skill.role.name == 'none' or skill.role.name == c.role.name:
            cskill = CharacterSkill()
            cskill.character = c
            cskill.skill = skill

            if skill.direction == INC:
                cskill.current = skill.minimum
            elif skill.direction == DEC:
                cskill.current = skill.maximum

            cskill.save()

    # initialize all character pointpools
    for p in Pointpool.objects.all():
        cpoints = CharacterPointpool()
        cpoints.character = c
        cpoints.pointpool = p
        cpoints.current = p.points
        cpoints.save()

    # begin spending points from character pointpools
    for cp in CharacterPointpool.objects.filter(character=c):
        cstats = CharacterStatistic.objects.filter(character=c).exclude(statistic__type=DEP)
        cskills = CharacterSkill.objects.filter(character=c)

        # subtract minimum points required to initialize stats and skills
        for cstat in cstats:
            if cstat.statistic.pointpool.name == cp.pointpool.name:
                if cstat.statistic.direction == INC:
                    for i in range(cstat.current):
                        cp.current -= cstat.statistic.cost * ( (i+1) ^ cstat.statistic.tier )
                        cp.save()
                elif cstat.statistic.direction == DEC:
                    for i in range(cstat.statistic.maximum - cstat.current):
                        cp.current -= cstat.statistic.cost * ( (i+1) ^ cstat.statistic.tier )
                        cp.save()

        for cskill in cskills:
            if cskill.skill.pointpool.name == cp.pointpool.name and ( cskill.skill.role.name == 'none' or cskill.skill.role.name == c.role.name ):
                for i in range(cskill.current):
                    cp.current -= cskill.skill.cost * ( (i+1) ^ cskill.skill.tier )
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
                    ( cstat.statistic.pointpool.name == cp.pointpool.name and cstat.statistic.type != DEP ) or
                    (
                    'roles' in tree and
                    'statpoints' in tree['roles'][c.role.name] and
                    tree['roles'][c.role.name]['statpoints'] == cp.pointpool.name and
                    cstat.statistic.name in tree['roles'][c.role.name]['stats']
                    )
                    ):

                if cstat.statistic.direction == INC and cstat.current < cstat.statistic.maximum:
                    cost = cstat.statistic.cost * ( (cstat.current+1) ^ cstat.statistic.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cstat.current += cstat.statistic.purchase
                        cstat.save()
                        cp.save()
                elif cstat.statistic.direction == DEC and cstat.current > cstat.statistic.minimum:
                    cost = cstat.statistic.cost * ( (cstat.statistic.maximum - cstat.current + 1) ^ cstat.statistic.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cstat.current -= cstat.statistic.purchase
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

                if cskill.skill.direction == INC and cskill.current < cskill.skill.maximum:
                    cost = cskill.skill.cost * ( (cskill.current+1) ^ cskill.skill.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cskill.current += cskill.skill.purchase
                        cskill.save()
                        cp.save()
                elif cskill.skill.direction == DEC and cskill.current > cskill.skill.minimum:
                    cost = cskill.skill.cost * ( (cskill.skill.maximum - cskill.current + 1) ^ cskill.skill.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cskill.current -= cskill.skill.purchase
                        cskill.save()
                        cp.save()

    if 'modifiers' in tree and 'points' in tree['modifiers']:
        for pointpool in tree['modifiers']['points']:
            for modifier_key in tree['modifiers']['points'][pointpool]:
                for modifier_lookup in tree['modifiers']['points'][pointpool][modifier_key]:
                    if modifier_key == 'stats':
                        cstat = CharacterStatistic.objects.filter(character=c).filter(statistic__name=modifier_lookup)
                        cp = CharacterPointpool.objects.filter(character=c).filter(pointpool__name=pointpool)
                        lookup = tree['modifiers']['points'][pointpool][modifier_key][modifier_lookup]

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
                            if cstat.current in roll_dict[str(key)]:
                                outcome = lookup[key]

                        if '+' in outcome:
                            addition = int(outcome.replace('+',''))
                            cp.current += addition
                            cp.save()
                        elif '-' in outcome:
                            subtraction = int(outcome.replace('-',''))
                            cp.current -= subtraction
                            cp.save()


if __name__ == '__main__':
    # character count to make per run
    character_count = 5

    skillstats_yaml = 'Examples/cyberpunk_2020/system_stats_skills.yaml'
    history_yaml = 'Examples/cyberpunk_2020/system_history.yaml'

    # needs error handling
    with open(history_yaml, 'r') as yamlfile:
        history = yaml.load(yamlfile)

    with open(skillstats_yaml,'r') as yamlfile:
        skillstats = yaml.load(yamlfile)

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

        roll(c, skillstats)

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

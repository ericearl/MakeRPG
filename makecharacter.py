import django, os, yaml, random, queue, time
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *

IND = 'I'
DEP = 'D'
TYPE_CHOICES = (
    (IND, 'independent'),
    (DEP, 'dependent'),
)


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
            cstat.current = stat.minimum
            cstat.save()

    # initialize all character skills
    for skill in Skill.objects.all():
        if skill.role.name == 'none' or skill.role.name == c.role.name:
            cskill = CharacterSkill()
            cskill.character = c
            cskill.skill = skill
            cskill.current = skill.minimum
            cskill.save()

    for p in Pointpool.objects.all():
        points = p.points
        cstats = CharacterStatistic.objects.filter(character=c).exclude(statistic__type=DEP)
        cskills = CharacterSkill.objects.filter(character=c)

        # subtract minimum points required to initialize stats and skills
        for cstat in cstats:
            if cstat.statistic.pointpool == p:
                points -= cstat.current

        for cskill in cskills:
            if cskill.skill.pointpool == p and ( cskill.skill.role.name == 'none' or cskill.skill.role.name == c.role.name ):

                points -= cskill.current

        # roll all character statistics and skills until their sum is "points"
        choosy = []
        if len(cstats) > 0:
            choosy.append('stat')
        if len(cskills) > 0:
            choosy.append('skill')

        while points > 0:
            if len(cstats) > 0:
                cstat = random.choice(cstats)
            if len(cskills) > 0:
                cskill = random.choice(cskills)

            choice = random.choice(choosy)

            if choice == 'stat' and (
                    ( cstat.statistic.pointpool == p and cstat.statistic.type != DEP ) or
                    (
                    'roles' in tree and
                    'statpoints' in tree['roles'][c.role.name] and
                    tree['roles'][c.role.name]['statpoints'] == p.name and
                    cstat.statistic.name in tree['roles'][c.role.name]['stats']
                    )
                    ) and cstat.current < cstat.statistic.maximum:

                cstat.current += 1
                points -= 1
                cstat.save()

            if choice == 'skill' and (
                    cskill.skill.pointpool == p or
                    (
                    'roles' in tree and
                    'skillpoints' in tree['roles'][c.role.name] and
                    tree['roles'][c.role.name]['skillpoints'] == p.name and
                    cskill.skill.name in tree['roles'][c.role.name]['skills']
                    )
                    ) and cskill.current < cskill.skill.maximum:

                cskill.current += 1
                points -= 1
                cskill.save()


if __name__ == '__main__':
    # character count to make per run
    character_count = 3

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

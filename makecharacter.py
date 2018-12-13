import django, os, yaml, random, queue, time
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *

def random_name(firstnames,lastnames):
    return ' '.join([ firstnames[random.randint(0, len(firstnames))] , lastnames[random.randint(0, len(lastnames))] ])


def get_history_starts(yaml_file):
    # needs error handling
    with open(yaml_file, 'r') as yamlfile:
        tree = yaml.load(yamlfile)

    if 'START' in tree and 'NPC' in tree:
        history_tree = tree
    else:
        print(yaml_file + ' is missing either START or NPC keywords.')
        return

    return (history_tree['START'], history_tree['NPC'][0])


def roll_stats(c):
    sp = c.stat_points

    # initialize all character statistics
    for stat in Statistic.objects.all().exclude(name='SPECIAL'):
        cstat = CharacterStatistic()
        cstat.character = c
        cstat.statistic = stat
        cstat.current = stat.minimum
        sp -= stat.minimum
        cstat.save()

    # roll all character statistics until their sum is stat points
    cstats = CharacterStatistic.objects.filter(character=c)
    while sp > 0:
        cstat = random.choice(cstats)
        if cstat.current < cstat.statistic.maximum:
            cstat.current += 1
            sp -= 1
            cstat.save()


def roll_skills(c):
    rp = c.role_points
    op = c.other_points

    # initialize skills
    special_skills = c.role.special_skills.all()
    common_skills = c.role.common_skills.all()
    role_skills = (special_skills | common_skills).distinct()
    special_stat = Statistic.objects.get(name='SPECIAL')
    all_special_skills = Skill.objects.filter(statistic=special_stat)
    other_skills = Skill.objects.all().difference(all_special_skills, role_skills)
    for skill in role_skills:
        cskill = CharacterSkill()
        cskill.character = c
        cskill.skill = skill
        cskill.current = skill.minimum
        rp -= skill.minimum
        cskill.save()

    role_cskills = CharacterSkill.objects.filter(character=c)
    while rp > 0:
        cskill = random.choice(role_cskills)
        if cskill.current < cskill.skill.maximum:
            cskill.current += 1
            rp -= 1
            cskill.save()

    for skill in other_skills:
        cskill = CharacterSkill()
        cskill.character = c
        cskill.skill = skill
        cskill.current = skill.minimum
        op -= skill.minimum
        cskill.save()

    other_cskills = CharacterSkill.objects.filter(
        character=c).difference(role_cskills)
    while op > 0:
        skill = random.choice(other_skills)
        cskill = CharacterSkill.objects.get(character=c, skill=skill)
        if cskill.current < cskill.skill.maximum:
            cskill.current += 1
            op -= 1
            cskill.save()


if __name__ == '__main__':
    # character count to make per run
    character_count = 5

    # mean (a.k.a. average) point values
    mean_stat_points = 40
    mean_role_points = 0
    mean_other_points = 20

    # percentage of mean variance
    mean_percentage = 20/100

    history_yaml = 'Examples/classless_cyberpunk_test/classless_cyberpunk_test_history.yaml'
    history_start, npc_start = get_history_starts(history_yaml)

    # names lists
    with open('MakeRPG/firstnames.txt', 'r') as firsts:
        firstnames = [name.strip('\n') for name in firsts.readlines()]
    with open('MakeRPG/lastnames.txt', 'r') as lasts:
        lastnames = [name.strip('\n') for name in lasts.readlines()]

    tstart = time.time()
    npc_count = 0
    for _ in range(character_count):
        char_tstart = time.time()

        # set points based on a normal distribution with a center mean and 20% mean variance
        # and don't let any points go below zero
        if mean_stat_points > 0:
            sp = round(random.normalvariate(mean_stat_points, mean_stat_points*mean_percentage))
            if sp < 0:
                sp = 0
        else:
            sp = 0

        if mean_role_points > 0:
            rp = round(random.normalvariate(mean_role_points, mean_role_points*mean_percentage))
            if rp < 0:
                rp = 0
        else:
            rp = 0

        if mean_other_points > 0:
            op = round(random.normalvariate(mean_other_points, mean_other_points*mean_percentage))
            if op < 0:
                op = 0
        else:
            op = 0

        c = Character()
        c.name = random_name(firstnames, lastnames)
        c.stat_points = sp
        c.role_points = rp
        c.other_points = op
        all_roles = Role.objects.all()
        if len(all_roles) > 0:
            c.role = random.choice(all_roles)
        c.save()

        roll_stats(c)
        roll_skills(c)

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

            # set points based on a normal distribution with a center mean and 20% mean variance
            # and don't let any points go below zero
            if mean_stat_points > 0:
                sp = round(random.normalvariate(mean_stat_points, mean_stat_points*mean_percentage))
                if sp < 0:
                    sp = 0
            else:
                sp = 0

            if mean_role_points > 0:
                rp = round(random.normalvariate(mean_role_points, mean_role_points*mean_percentage))
                if rp < 0:
                    rp = 0
            else:
                rp = 0

            if mean_other_points > 0:
                op = round(random.normalvariate(mean_other_points, mean_other_points*mean_percentage))
                if op < 0:
                    op = 0
            else:
                op = 0

            npc = Character()
            npc.name = '[NPC ' + npc_q.get() + '] ' + random_name(firstnames, lastnames)
            npc.stat_points = sp
            npc.role_points = rp
            npc.other_points = op
            if len(all_roles) > 0:
                npc.role = random.choice(all_roles)
            npc.save()

            roll_stats(npc)
            roll_skills(npc)

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

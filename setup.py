import django, os, yaml, random, string, urllib.request, queue, re, sys, time, csv
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *

def random_name(firstnames,lastnames):
    return ' '.join([ firstnames[random.randint(0, len(firstnames))] , lastnames[random.randint(0, len(lastnames))] ])

def setup_skillstats(yaml_file):
    # needs error handling
    with open(yaml_file,'r') as yamlfile:
        tree = yaml.load(yamlfile)

    if 'roles' in tree and 'stats' in tree:
        sp = Statistic()
        sp.name = 'SPECIAL'
        sp.save()
        
        for stat in tree['stats'].keys():
            statmin,statmax = (int(number) for number in tree['stats'][stat]['stat'].split('-'))
            st = Statistic()
            st.name = stat
            st.minimum = statmin
            st.maximum = statmax
            st.save()
            
            if 'skills' in tree['stats'][stat]:
                for skill in tree['stats'][stat]['skills'].keys():
                    skillmin,skillmax = (int(number) for number in tree['stats'][stat]['skills'][skill].split('-'))
                    sk = Skill()
                    sk.name = skill
                    sk.minimum = skillmin
                    sk.maximum = skillmax
                    sk.statistic = st
                    sk.save()
        
        for role in tree['roles'].keys():
            r = Role()
            r.name = role
            r.save()
            
            for special in tree['roles'][role]['special'].keys():
                specialmin,specialmax = (int(number) for number in tree['roles'][role]['special'][special].split('-'))
                spsk = Skill()
                spsk.name = special
                spsk.minimum = specialmin
                spsk.maximum = specialmax
                spsk.statistic = sp
                spsk.save()
                r.special_skills.add(spsk)
            
            for common in tree['roles'][role]['common']:
                r.common_skills.add( Skill.objects.get(name=common) )
            
            r.save()

    else:
        print(yaml_file + ' is missing either roles or stats keywords.')


def setup_history(yaml_file):
    # needs error handling
    with open(yaml_file,'r') as yamlfile:
        tree = yaml.load(yamlfile)

    if 'START' in tree and 'NPC' in tree:
        history_tree = tree
    else:
        print(yaml_file + ' is missing either START or NPC keywords.')
        return

    start = history_tree['START']

    dice_list = []
    for event in history_tree.keys():
        if event != 'START' and event != 'NPC':
            dice_list.append(history_tree[event]['dice'])

    print('MAKING DICE')
    unique_dice = set(dice_list)
    for dice_str in unique_dice:
        search = re.match(r'([0-9]+)d([0-9]+)\ *(\+|-)*\ *([0-9]*)',dice_str)
        quantity = int(search.group(1))
        sides = int(search.group(2))
        if search.group(3) == None:
            offset = 0
        else:
            offset = int(search.group(3)+search.group(4))

        d = Dice()
        d.string = dice_str
        d.quantity = quantity
        d.sides = sides
        d.offset = offset
        d.save()

    print('MAKING EVENTS')
    for event in history_tree.keys():
        if event != 'START' and event != 'NPC':
            dice = Dice.objects.get(string=history_tree[event]['dice'])
            e = Event()
            e.name = event
            e.dice = dice
            e.save()

    for event in history_tree.keys():
        if event != 'START' and event != 'NPC':
            print('POPULATING EVENT: ' + event)
            e = Event.objects.get(name=event)
            d = e.dice
            dice_min = d.quantity + d.offset
            dice_max = d.quantity * d.sides + d.offset
            dice_span = list(range(dice_min,dice_max+1))

            if 'next' in history_tree[event]:
                e.nextevent = Event.objects.get(name=history_tree[event]['next'])
                e.save()
            elif 'reroll' in history_tree[event]:
                e.rerollevent = Event.objects.get(name=history_tree[event]['reroll'])
                e.save()

            rolls = history_tree[event]['roll']
            if 'EVEN' in rolls and 'ODD' in rolls and len(rolls) == 2:
                for number in dice_span:
                    er = EventRoll()
                    er.mainevent = e
                    er.roll = number

                    if number % 2 == 0:
                        at_roll = rolls['EVEN']
                    else:
                        at_roll = rolls['ODD']
                    if type(at_roll)==dict and 'next' in at_roll:
                        er.rollevent = Event.objects.get(name=at_roll['next'])
                        er.save()
                    elif type(at_roll)==str:
                        er.outcome = at_roll
                        er.save()

            else:
                possible_rolls = []
                # a dictionary of roll value lists whose keys are roll strings
                roll_dict = {}
                for element in rolls.keys():
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

                if len(possible_rolls) < len(dice_span):
                    print('Too few possible rolls in ' + str(rolls))
                    sys.exit()
                elif len(possible_rolls) > len(dice_span):
                    print('Too many possible rolls in ' + str(rolls))
                    sys.exit()
                elif sorted(possible_rolls) == dice_span:

                    for roll in possible_rolls:
                        er = EventRoll()
                        er.mainevent = e
                        er.roll = roll

                        for key in rolls.keys():
                            if roll in roll_dict[str(key)]:
                                outcome = rolls[key]

                                if type(outcome) is dict and 'next' in outcome:
                                    outcome = outcome['next']
                                    if '<NPC' in outcome:
                                        npc_match = re.match(r'(.*)<NPC\ *(.+)>\ *(.+)',outcome)
                                        er.npc = npc_match.group(2)
                                        outcome = npc_match.group(1) + npc_match.group(3)

                                    if '<ROLL X' in outcome:
                                        roll_x = re.match(r'(.*)<ROLL\ *X([0-9]+)>\ *(.+)',outcome)
                                        er.rerollcount = int(roll_x.group(2))
                                        outcome = roll_x.group(1) + roll_x.group(3)

                                    er.rollevent = Event.objects.get(name=outcome)
                                    er.save()

                                elif type(outcome) is str:
                                    if '<NPC' in outcome:
                                        npc_match = re.match(r'(.*)<NPC\ *(.+)>\ *(.+)',outcome)
                                        er.npc = npc_match.group(2)
                                        outcome = npc_match.group(1) + npc_match.group(3)

                                    if '<ROLL X' in outcome:
                                        roll_x = re.match(r'(.*)<ROLL\ *X([0-9]+)>\ *(.+)',outcome)
                                        er.rerollcount = int(roll_x.group(2))
                                        outcome = roll_x.group(1) + roll_x.group(3)

                                    er.outcome = outcome
                                    er.save()

                                break

                else:
                    print('Possible rolls and dice span do not match in ' + str(rolls))
                    sys.exit()

    npc_order = history_tree['NPC']

    if type(npc_order) is list and len(npc_order)>1:
        for i,next_event in enumerate(npc_order[1:]):
            current_event = npc_order[i]
            n = NPCEvent()
            n.current = Event.objects.get(name=current_event)
            n.next = Event.objects.get(name=next_event)
            n.save()


def get_history_starts(yaml_file):
    # needs error handling
    with open(yaml_file,'r') as yamlfile:
        tree = yaml.load(yamlfile)

    if 'START' in tree and 'NPC' in tree:
        history_tree = tree
    else:
        print(yaml_file + ' is missing either START or NPC keywords.')
        return

    return ( history_tree['START'] , history_tree['NPC'][0] )


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
    role_skills = ( special_skills | common_skills ).distinct()
    special_stat = Statistic.objects.get(name='SPECIAL')
    all_special_skills = Skill.objects.filter(statistic=special_stat)
    other_skills = Skill.objects.all().difference(all_special_skills,role_skills)
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
            cskill.current +=1
            rp -= 1
            cskill.save()

    for skill in other_skills:
        cskill = CharacterSkill()
        cskill.character = c
        cskill.skill = skill
        cskill.current = skill.minimum
        op -= skill.minimum
        cskill.save()

    other_cskills = CharacterSkill.objects.filter(character=c).difference(role_cskills)
    while op > 0:
        skill = random.choice(other_skills)
        cskill = CharacterSkill.objects.get(character=c, skill=skill)
        if cskill.current < cskill.skill.maximum:
            cskill.current += 1
            op -= 1
            cskill.save()


if __name__ == '__main__':
    character_count = 5
    center_stat_points = 50
    center_role_points = 40
    center_other_points = 10
    # skillstats_yaml = 'C:/Users/Eric/Documents/Hobby/CharGen/cyberpunk_2020_stats_skills.yml'
    # history_yaml = 'C:/Users/Eric/Documents/Hobby/CharGen/cyberpunk_2020_history.yml'
    skillstats_yaml = 'C:/Users/erice/Google Drive/Hobby/CharGen/cyberpunk_2020_stats_skills.yml'
    history_yaml = 'C:/Users/erice/Google Drive/Hobby/CharGen/cyberpunk_2020_history.yml'
    history_start, npc_start = get_history_starts(history_yaml)

    # # ONE-TIME roles, stats, and skills definitions ONLY HAPPENS ONCE
    # setup_skillstats(skillstats_yaml)

    # # ONE-TIME history events and rolls definitions ONLY HAPPENS ONCE
    # setup_history(history_yaml)

    # names lists
    with open('MakeRPG/firstnames.txt','r') as firsts:
        firstnames = [name.strip('\n') for name in firsts.readlines()]
    with open('MakeRPG/lastnames.txt','r') as lasts:
        lastnames = [name.strip('\n') for name in lasts.readlines()]

    tstart = time.time()
    npc_count = 0
    for _ in range(character_count):
        char_tstart = time.time()
        sp = round(random.normalvariate(center_stat_points,center_stat_points/5))
        rp = round(random.normalvariate(center_role_points,center_role_points/5))
        op = round(random.normalvariate(center_other_points,center_other_points/5))

        c = Character()
        c.name = random_name(firstnames,lastnames)
        c.stat_points = sp
        c.role_points = rp
        c.other_points = op
        c.role = random.choice(Role.objects.all())
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
            sp = round(random.normalvariate(center_stat_points,center_stat_points/5))
            rp = round(random.normalvariate(center_role_points,center_role_points/5))
            op = round(random.normalvariate(center_other_points,center_other_points/5))

            npc = Character()
            npc.name = '[NPC ' + npc_q.get() + '] ' + random_name(firstnames,lastnames)
            npc.stat_points = sp
            npc.role_points = rp
            npc.other_points = op
            npc.role = random.choice(Role.objects.all())
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
            print('%s made in %0.1f seconds' % (npc,npc_tstop-npc_tstart))

        char_tstop = time.time()
        print('%s made in %0.1f seconds' % (c,char_tstop-char_tstart))

    tstop = time.time()

    elapsed_time = tstop - tstart
    avg_character_time = elapsed_time / character_count
    avg_character_npc_time = elapsed_time / (character_count + npc_count)

    print( 'Created %d character(s) and %d NPC(s) in %0.2f minutes' % (character_count,npc_count,elapsed_time/60) )
    print( 'Average full character with NPC(s) time: %0.1f seconds' % (avg_character_time) )
    print( 'Average time per character or NPC: %0.1f seconds' % (avg_character_npc_time) )


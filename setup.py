import django, os, yaml, re, sys
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *


# class HistoryEventError(Exception):
#     def __init__(self, name):
#         self.name = name
#     print(self.name + ' not present')
#     raise


def validate_skillstats(yaml_file):
    print('Validating Skills & Stats YAML: ' + yaml_file)

    with open(yaml_file, 'r') as yamlfile:
        tree = yaml.load(yamlfile)

    error_flag = False

    if 'stats' not in tree.keys():
        print('ERROR: Missing required stats keyword up top')
        error_flag = True

    skill_collection = []
    for stat in tree['stats'].keys():
        substat = tree['stats'][stat]

        if 'stat' not in substat:
            print('ERROR: stat keyword not in [stats > ' + stat + ']')
            error_flag = True
        else:
            # improve with re non-hyphen + non-numeric tests
            value_range = [int(value) for value in substat['stat'].split('-')]
            prefix = 'ERROR: stat range (' + substat['stat'] + ') in [stats > ' + stat + ' > stat]'
            if len(value_range) < 2:
                print(prefix + ' has less than two hyphenated values')
                error_flag = True
            elif len(value_range) > 2:
                print(prefix + ' has greater than two hyphenated values')
                error_flag = True
            elif value_range[0] > value_range[1]:
                print(prefix + ' contains a larger first number (' + str(value_range[0]) + ') than second number (' + str(value_range[1]) + ')')
                error_flag = True

        if 'skills' not in substat:
            print('WARNING: skills keyword not in [stats > ' + stat + ']')
        else:
            for skill in substat['skills'].keys():
                subskill = substat['skills'][skill]
                value_range = [int(value) for value in subskill.split('-')]
                prefix = 'ERROR: skill range (' + subskill + ') in [stats > ' + stat + ' > skills > ' + skill + ']'
                if len(value_range) < 2:
                    print(prefix + ' has less than two hyphenated values')
                    error_flag = True
                elif len(value_range) > 2:
                    print(prefix + ' has greater than two hyphenated values')
                    error_flag = True
                elif value_range[0] > value_range[1]:
                    print(prefix + ' contains a larger first number (' + str(value_range[0]) + ') than second number (' + str(value_range[1]) + ')')
                    error_flag = True
                skill_collection.append(skill)

    if 'roles' in tree.keys():
        for role in tree['roles'].keys():
            subrole = tree['roles'][role]
            if 'special' not in subrole:
                print('ERROR: special keyword not in [roles > ' + role + ']')
                error_flag = True
            if 'common' not in subrole:
                print('ERROR: common keyword not in [roles > ' + role + ']')
                error_flag = True
            
            for special in subrole['special'].keys():
                subspecial = subrole['special'][special]
                value_range = [int(value) for value in subspecial.split('-')]
                prefix = 'ERROR: special range (' + subspecial + ') in [roles > ' + role + ' > special > ' + special + ']'
                if len(value_range) < 2:
                    print(prefix + ' has less than two hyphenated values')
                    error_flag = True
                elif len(value_range) > 2:
                    print(prefix + ' has greater than two hyphenated values')
                    error_flag = True
                elif value_range[0] > value_range[1]:
                    print(prefix + ' contains a larger first number (' + str(value_range[0]) + ') than second number (' + str(value_range[1]) + ')')
                    error_flag = True

            for common in subrole['common']:
                if common not in skill_collection:
                    print('ERROR: [roles > ' + role + ' > common > ' + common + '] not among all common skills:')
                    print(skill_collection)
                    error_flag = True

    if error_flag:
        return False
    else:
        print('Valid Skills & Stats YAML!')
        return True


def validate_history(yaml_file):
    print('Validating History YAML: ' + yaml_file)

    with open(yaml_file, 'r') as yamlfile:
        tree = yaml.load(yamlfile)

    events = list(tree.keys())
    error_flag = False

    if 'START' not in events:
        print('ERROR: Missing required START keyword up top')
        error_flag = True

    if 'NPC' not in events:
        print('ERROR: Missing required NPC keyword up top')
        error_flag = True

    events.remove('START')
    events.remove('NPC')

    reroll_list = []

    for event in events:
        event_dict = tree[event]

        if 'dice' not in event_dict:
            print('ERROR: dice keyword not in event ' + event)
            error_flag = True
        if 'roll' not in event_dict:
            print('ERROR: roll keyword not in event ' + event)
            error_flag = True

        dice = event_dict['dice']
        search = re.match(r'([0-9]+)d([0-9]+)\ *(\+|-)*\ *([0-9]*)', dice)
        if search.group(1) == None and search.group(2) == None:
            print('ERROR: Invalid dice (' + dice + ') for event ' + event)
            error_flag = True

        quantity = int(search.group(1))
        sides = int(search.group(2))
        if search.group(3) == None:
            offset = 0
        else:
            offset = int(search.group(3)+search.group(4))

        dice_min = quantity + offset
        dice_max = quantity * sides + offset
        dice_span = list(range(dice_min, dice_max+1))

        rolls = event_dict['roll']

        if 'EVEN' in rolls and 'ODD' not in rolls and len(rolls) == 2:
            print('ERROR: EVEN in roll, but no ODD in roll for event ' + event)
            error_flag = True
        elif 'EVEN' not in rolls and 'ODD' in rolls and len(rolls) == 2:
            print('ERROR: ODD in roll, but no EVEN in roll for event ' + event)
            error_flag = True
        elif 'EVEN' in rolls and 'ODD' in rolls and len(rolls) > 2:
            print('ERROR: EVEN and ODD keywords used, but there are more than two keywords in event ' + event)
            error_flag = True
        elif 'EVEN' not in rolls and 'ODD' not in rolls:
            possible_rolls = []
            # a dictionary of roll value lists whose keys are roll strings
            for element in rolls.keys():
                roll_str = str(element)

                if '-' not in roll_str and ',' not in roll_str:
                    # a single value
                    values = int(roll_str)
                    possible_rolls.append(values)
                elif ',' in roll_str:
                    # multiple values
                    for partial in roll_str.split(','):
                        if '-' in partial:
                            # a span of comma-separated values
                            minimum,maximum = (int(number) for number in partial.split('-'))
                            values = list(range(minimum,maximum+1))
                            possible_rolls += values
                        else:
                            # a single comma-separated value
                            values = int(partial)
                            possible_rolls.append(values)
                elif '-' in roll_str:
                    # a span of values
                    minimum,maximum = (int(number) for number in roll_str.split('-'))
                    values = list(range(minimum,maximum+1))
                    possible_rolls += values

            if len(possible_rolls) < len(dice_span):
                print('ERROR: Too few possible rolls in ' + str(rolls) + ' for event ' + event)
                error_flag = True
            elif len(possible_rolls) > len(dice_span):
                print('ERROR: Too many possible rolls in ' + str(rolls) + ' for event ' + event)
                error_flag = True
            elif sorted(possible_rolls) != dice_span:
                print('ERROR: possible rolls (' + possible_rolls + ') does not match dice span (' + dice_span + ') for event ' + event)
                error_flag = True

            if 'next' in event_dict:
                if event_dict['next'] not in events:
                    print('ERROR: next event (' + event_dict['next'] + ') does not exist for event ' + event)
                    error_flag = True

            for roll in rolls.keys():
                outcome = rolls[roll]
                if type(outcome) is dict:
                    for key in outcome.keys():
                        if key != 'next':
                            print('ERROR: Invalid keyword (' + key + ') for roll ' + str(roll) + ' in event ' + event)
                            error_flag = True
                        else:
                            outcome = outcome['next']

                            if '<NPC' in outcome:
                                npc_match = re.match(r'(.*)<NPC\ *(.+)>\ *(.+)', outcome)
                                outcome = npc_match.group(1) + npc_match.group(3)

                            if '<ROLL X' in outcome:
                                roll_x = re.match(r'(.*)<ROLL\ *X([0-9]+)>\ *(.+)', outcome)
                                outcome = roll_x.group(1) + roll_x.group(3)
                                reroll_list.append(outcome)

                            if outcome not in events:
                                print('ERROR: next event (' + outcome + ') does not exist for roll ' + str(roll) + ' in event ' + event)
                                error_flag = True

                elif type(outcome) is str:
                    if '<NPC' in outcome:
                        npc_match = re.match(r'(.*)<NPC\ *(.+)>\ *(.+)', outcome)
                        outcome = npc_match.group(1) + npc_match.group(3)

                    if '<ROLL X' in outcome:
                        roll_x = re.match(r'(.*)<ROLL\ *X([0-9]+)>\ *(.+)', outcome)
                        outcome = roll_x.group(1) + roll_x.group(3)
                        reroll_list.append(outcome)

                else:
                    print('ERROR: Outcome is neither a next key-value pair nor a string for roll ' + str(roll) + ' in event ' + event)
                    error_flag = True

    reroll_set = set(reroll_list)
    for event in events:
        event_dict = tree[event]
        if 'reroll' in event_dict:
            reroll_event = event_dict['reroll']
            if reroll_event in reroll_set:
                reroll_set.remove(reroll_event)
            else:
                print('ERROR: reroll event (' + reroll_event + ') does not exist in any <ROLL X#> tag for event ' + event)
                error_flag = True

    if len(reroll_set) != 0:
        print('ERROR: Unmatched reroll(s) among all <ROLL X#> tags: ' + str(reroll_set))
        error_flag = True

    if error_flag:
        return False
    else:
        print('Valid History YAML!')
        return True


def setup_skillstats(yaml_file):
    # needs error handling
    with open(yaml_file,'r') as yamlfile:
        tree = yaml.load(yamlfile)

    if 'stats' not in tree:
        print(yaml_file + ' is missing stats keyword.')
        return

    else:
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

    if 'roles' in tree:
        sp = Statistic()
        sp.name = 'SPECIAL'
        sp.save()

        for role in tree['roles'].keys():
            r = Role()
            r.name = role
            r.save()

            if 'special' in tree['roles'][role]:
                for special in tree['roles'][role]['special'].keys():
                    specialmin,specialmax = (int(number) for number in tree['roles'][role]['special'][special].split('-'))
                    spsk = Skill()
                    spsk.name = special
                    spsk.minimum = specialmin
                    spsk.maximum = specialmax
                    spsk.statistic = sp
                    spsk.save()
                    r.special_skills.add(spsk)

            if 'common' in tree['roles'][role]:
                for common in tree['roles'][role]['common']:
                    r.common_skills.add( Skill.objects.get(name=common) )

            r.save()


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


if __name__ == '__main__':
    skillstats_yaml = 'Examples/system_stats_skills.yaml'
    history_yaml = 'Examples/system_history.yaml'

    valid_skillstats = validate_skillstats(skillstats_yaml)
    valid_history = validate_history(history_yaml)

    if not valid_skillstats:
        print('Skils & Stats YAML had at least one ERROR, review this output and correct all errors')

    if not valid_history:
        print('History YAML had at least one ERROR, review this output and correct all errors')
    
    if not valid_skillstats or not valid_history:
        print('Quitting without setting up game system database')
    else:
        print('Setting up game system database')
        # ONE-TIME roles, stats, and skills definitions ONLY HAPPENS ONCE
        # This should only be run once
        # If it fails somehow, you should empty your database, adjust your YAML's, and try again
        setup_skillstats(skillstats_yaml) # comment this out when you're done with it

        # ONE-TIME history events and rolls definitions ONLY HAPPENS ONCE
        # This should only be run once
        # If it fails somehow, you should empty your database, adjust your YAML's, and try again
        setup_history(history_yaml) # comment this out when you're done with it
        print('Successfully completed setup.py!  Proceed to makecharacter.py...')

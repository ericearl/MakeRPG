import django, os, yaml, re, sys
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MakeRPG.settings")
django.setup()

from CharacterCreator.models import *

TYPES = {
    'independent': 'I',
    'dependent': 'D'
}

TIERS = {
    'add': 0,
    'multiply': 1,
    'double': 2,
    'triple': 3,
    'quadruple': 4,
    'quintuple': 5,
    'sextuple': 6,
    'septuple': 7,
    'octuple': 8,
    'nonuple': 9,
    'decuple': 10
}

# Support for the MakeRPG YAML lookup language
# dice:
    # '[0-9]+d[0-9]+\ *(>|<)*'
# lookup:
    # '<([\w\ \.\-])+>' = ordered-lookup
    # '<.>' = parent-lookup
    # '<<(stat|skill)>>' = nested-lookup
# math:
    # '\ \+\ ' = add
    # '\ \-\ ' = subtract
    # '\ \*\ ' = multiply
    # '\ \/\ ' = divide
# functions( lookups, logicals, and/or math ) = function
    # '\((\ lookup,*)+\ \)' = logical functions:
        # 'min\((\ lookup,*)+\ \)' = minimum of csv's
        # 'max\((\ lookup,*)+\ \)' = maximum of csv's
    # '\(\ lookup\ math\ lookup\ \)' = math functions:
        # 'exact\(\ lookup\ \)' = keep as fractional if fractional
        # 'round\(\ lookup\ \)' = round regularly if fractional
        # 'roundup\(\ lookup\ \)' = round up if fractional
        # 'rounddown\(\ lookup\ \)' = round down if fractional
    # '\ \(\ .+\ \)\ ' = inner evaluations
    # '\ .+\ <\ .+\ ' = less than
    # '\ .+\ >\ .+\ ' = greater than
    # 'AND'
    # 'OR'
    # '.+\ WHERE\ .+\ IS\ .+'
# ORDER OF OPERATIONS
# 1. options:
# 2. defaults:
# 3. stats:
# 4. parentheses
# . multiplication
# . division
# . addition
# . subtraction
# . ordered-lookup

# def ordered_lookup(tree, branch, line):
#     lookup_list = line.split(' ')

#     lookup = lookup_list.pop(0)
#     new_lookup = lookup
#     while '<' in lookup and '>' in lookup:
#         if '<<stat>>' == lookup or '<<skill>>' == lookup:
#             nested_lookup(tree, branch, line)
#         elif '<.>' == lookup:
#             # throw away one branch depth to get parent
#             parent_lookup(tree, branch[:-1], line)
#         else:
#             lookup = lookup_list.pop(0)
#             new_lookup += ' ' + lookup

#     new_lookup_list = new_lookup.replace('<', '').replace('>', '').split(' ')

#     new_branch = new_lookup_list
#     new_lookup = new_lookup_list.pop(0)
#     tree_lookup = tree[new_lookup]
#     while len(new_lookup_list) > 0:
#         new_lookup = new_lookup_list.pop(0)
#         tree_lookup = tree_lookup[new_lookup]

#     parse(tree, new_branch, tree_lookup)
#     return

# def parent_lookup(tree, branch, line):
#     lookup_list = line.split(' ')

#     lookup = lookup_list.pop(0)
#     new_lookup = lookup
#     while '<' in lookup and '>' in lookup:
#         # lookup = lookup_list.pop(0)
#         # grandparent = re.replace(r'(.+)\ <.+>',group1)
#         # parent = branch
#         # parse(tree, grandparent, line)
#     return

# def nested_lookup(tree, branch, line):
#     lookup_list = line.split(' ')

#     lookup = lookup_list.pop(0)
#     new_lookup = lookup
#     while '<' in lookup and '>' in lookup:
#         if '<<stat>>' == lookup:
#             for stat in tree['stats'].keys():
#                 continue
#                 # if stat in branch:
#                     # forced lookup of relevant stat
#         elif '<<skill>>' == lookup:
#             for skill in tree['skills'].keys():
#                 continue
#                 # if skill in branch:
#                     # forced lookup of relevant skill
#     return

# def maths(tree, branch, line):
#     return

# def functions(tree, branch, line):
#     if line.startswith('min('):
#         continue
#     elif line.startswith('max('):
#         continue
#     elif line.startswith('exact('):
#         continue
#     elif line.startswith('round('):
#         continue
#     elif line.startswith('roundup('):
#         continue
#     elif line.startswith('rounddown('):
#         continue

#     return

# def parentheses(tree, branch, line):
#     open_p = re.finditer(r'\(', line)
#     close_p = re.finditer(r'\)', line)
#     pstarts = [p.start() for p in open_p]
#     pstops = [p.end() for p in close_p]
#     if len(open_p) > 0 and len(open_p) == len(close_p):
#         pairs = []
#         while len(pstarts) > 0:
#             pstart = pstarts.pop()
#             for i, elem in enumerate(pstops):
#                 if elem > pstart:
#                     pstop = pstops.pop(i)
#                     break
#             pairs.append((pstart, pstop))

#         sublines = []
#         for pair in pairs:
#             subline = line[pair[0]+1:pair[1]]
#             sublines.append(subline)

#         parent_childs = []
#         for i, subline1 in enumerate(sublines):
#             for j, subline2 in enumerate(sublines):
#                 if j > i:
#                     # i,j: (0,1) (0,2) (0,3) (1,2) (1,3) (2,3)
#                     # P->C: (1,0) (3,0) (3,1) (3,2)
#                     if subline2 in subline1:
#                         # 1 = parent, 2 = child
#                         parent_childs.append((i, j))
#                     elif subline1 in subline2:
#                         # 2 = parent, 1 = child
#                         parent_childs.append((j, i))

#         # score_parents: [0,1,0,3]
#         score_parents = [0 for _ in range(len(pairs))]
#         for parent_idx, child_idx in parent_childs:
#             score_parents[parent_idx] += 1

#         newline = line
#         for i, pair in enumerate(pairs):
#             for score in score_parents:
#                 if score == i:
#                     subline = line[pair[0]+1:pair[1]]
#                     replaceline = parse(tree, branch, subline)
#                     newline.replace('('+subline+')', replaceline)
#     return

# def parse(tree, branch, line):
#     parseable_re = re.compile(r'<(\.|stats|skills|points|defaults|options)>|\d+d\d+|\(\ .+\ \)')
#     dice_re = re.compile('([0-9]+)d([0-9]+)')
#     lookup_re = re.compile('<([\w\ \.\-])+>')

#     if type(line) is int:
#         return line

#     elif type(line) is str and parseable_re.search(line) != None:
#         # example: Z - ( 6 * ( 8 + 9 ) - roundup( min( X , Y ) / 2 ) )
#         # O:[1,2,4,5] C:[3,6,7,8]
#         # P:[(5,6),(4,7),(2,3),(1,8)]
#         open_p = re.finditer(r'\(', line)
#         close_p = re.finditer(r'\)', line)
#         pstarts = [p.start() for p in open_p]
#         pstops = [p.end() for p in close_p]

#         if len(open_p) > 0 and len(open_p) == len(close_p):
#             parentheses(tree, branch, line)

#         else:
#             ordered_lookup(tree, branch, line)


# For modifiers keys
# def modkeyparse(tree, line, parent):
#     return parse(tree, '<modifiers> <' + parent + '>', ' < ' + parent + ' > ' + line)


def parse_dice(dice_str):
    print(dice_str)
    search = re.match(r'([0-9]+)d([0-9]+)\ *(\+|-)*\ *(stat|[0-9]*)', dice_str)
    if search.group(1) == None and search.group(2) == None:
        print('ERROR: Invalid dice (' + dice_str + ') for event ' + event)
        # error_flag = True

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
        quantity, sides, offset, dice_span = parse_dice(dice)

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


def save_skillstat(s,
                    name,
                    minimum,
                    maximum,
                    direction,
                    cost,
                    purchase,
                    tier,
                    s_type,
                    role,
                    pointpool):
    s.name = name
    s.minimum = minimum
    s.maximum = maximum
    s.direction = direction
    s.cost = cost
    s.purchase = purchase
    s.tier = tier
    s.type = s_type
    s.role = role
    s.pointpool = pointpool
    s.save()


def setup_skillstats(yaml_file):
    # needs error handling
    with open(yaml_file,'r') as yamlfile:
        tree = yaml.load(yamlfile)

    r = Role()
    r.name = 'none'
    r.save()

    p = Pointpool()
    p.name = 'roll'
    p.points = 0
    p.save()

    if 'roles' in tree:
        for role in tree['roles'].keys():
            r = Role()
            r.name = role
            r.save()

    for pointpool in tree['points']:
        p = Pointpool()
        p.name = pointpool
        p.points = tree['points'][pointpool]['set']
        p.save()
    
    defstat = tree['defaults']['stats']
    defskill = tree['defaults']['skills']

    for flavor in ['stats','skills']:
        for kind in tree[flavor].keys():
            definition = tree[flavor][kind]
            kinds = {}

            for key in ['range', 'direction', 'cost', 'purchase', 'tier', 'type', 'role', 'points']:
                if type(definition) is dict and key in definition:
                    kinds[key] = definition[key]
                elif flavor == 'stats':
                    kinds[key] = defstat[key]
                elif flavor == 'skills':
                    kinds[key] = defskill[key]

            if type(kinds['range']) is str:
                if kinds['range'][0] == '-':
                    pos_minimum, maximum = (int(number) for number in kinds['range'][1:].split('-'))
                    minimum = pos_minimum * (-1)
                else:
                    minimum, maximum = (int(number) for number in kinds['range'].split('-'))
            elif type(kinds['range']) is int:
                minimum = kinds['range']
                maximum = kinds['range']

            if type(kinds['purchase']) == int:
                dice_str = '0d0 + ' + str(kinds['purchase'])
            elif type(kinds['purchase']) == str:
                dice_str = kinds['purchase']

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

            if flavor == 'stats':
                s = Statistic()
                save_skillstat(s, 
                    name=kind,
                    minimum=minimum,
                    maximum=maximum,
                    direction=kinds['direction'],
                    cost=kinds['cost'],
                    purchase=d,
                    tier=TIERS[kinds['tier']],
                    s_type=TYPES[kinds['type']],
                    role=Role.objects.get(name=kinds['role']),
                    pointpool=Pointpool.objects.get(name=kinds['points']))
            elif flavor == 'skills':
                stat_str = tree[flavor][kind]['stat']
                if 'stat' in dice_str:
                    if (stat_str[:4] == 'min(' or stat_str[:4] == 'max(') and stat_str[-1] == ')':
                        for stat in stat_str[4:-1].split('|'):
                            skillstat = Statistic.objects.get(name=stat)
                            s = Skill()
                            s.statistic = skillstat
                            save_skillstat(s, 
                                name=kind,
                                minimum=minimum,
                                maximum=maximum,
                                direction=kinds['direction'],
                                cost=kinds['cost'],
                                purchase=d,
                                tier=TIERS[kinds['tier']],
                                s_type=TYPES[kinds['type']],
                                role=Role.objects.get(name=kinds['role']),
                                pointpool=Pointpool.objects.get(name=kinds['points']))
                    else:
                        skillstat = Statistic.objects.get(name=stat_str)
                        if 'stat' in tree[flavor][kind]:
                            s = Skill()
                            s.statistic = skillstat
                            save_skillstat(s, 
                                name=kind,
                                minimum=minimum,
                                maximum=maximum,
                                direction=kinds['direction'],
                                cost=kinds['cost'],
                                purchase=d,
                                tier=TIERS[kinds['tier']],
                                s_type=TYPES[kinds['type']],
                                role=Role.objects.get(name=kinds['role']),
                                pointpool=Pointpool.objects.get(name=kinds['points']))

                else:
                    skillstat = Statistic.objects.get(name=stat_str)
                    if 'stat' in tree[flavor][kind]:
                        s = Skill()
                        s.statistic = skillstat
                        save_skillstat(s, 
                            name=kind,
                            minimum=minimum,
                            maximum=maximum,
                            direction=kinds['direction'],
                            cost=kinds['cost'],
                            purchase=d,
                            tier=TIERS[kinds['tier']],
                            s_type=TYPES[kinds['type']],
                            role=Role.objects.get(name=kinds['role']),
                            pointpool=Pointpool.objects.get(name=kinds['points']))


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
    skillstats_yaml = 'Examples/aces_and_eights/system_stats_skills.yaml'
    history_yaml = 'Examples/aces_and_eights/system_history.yaml'

    # valid_skillstats = validate_skillstats(skillstats_yaml)
    valid_history = validate_history(history_yaml)

    # if not valid_skillstats:
    #     print('Skils & Stats YAML had at least one ERROR, review this output and correct all errors')

    if not valid_history:
        print('History YAML had at least one ERROR, review this output and correct all errors')
    
    # if not valid_skillstats or not valid_history:
    #     print('Quitting without setting up game system database')
    # else:
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

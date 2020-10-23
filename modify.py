from CharacterCreator.models import *

# apply modifiers
def modify(c, tree, modifier):
    for being_modified in tree['modifiers'][modifier]:
        for modifier_key in tree['modifiers'][modifier][being_modified]:
            for modifier_lookup in tree['modifiers'][modifier][being_modified][modifier_key]:
                if modifier_key == 'stats':
                    cs = CharacterStatistic.objects.filter(character=c).get(statistic__name=modifier_lookup)
                elif modifier_key == 'skills':
                    cs = CharacterSkill.objects.filter(character=c).get(skill__name=modifier_lookup)
                elif modifier_key == 'traits':
                    cs = CharacterTrait.objects.filter(character=c).get(trait__name=modifier_lookup)

                if modifier == 'points':
                    cx = CharacterPointpool.objects.filter(character=c).get(pointpool__name=being_modified)
                elif modifier == 'stats':
                    cx = CharacterStatistic.objects.filter(character=c).get(statistic__name=being_modified)
                elif modifier == 'skills':
                    cx = CharacterSkill.objects.filter(character=c).get(skill__name=being_modified)
                elif modifier == 'traits':
                    cx = CharacterTrait.objects.filter(character=c).get(trait__name=being_modified)

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

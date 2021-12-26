import random

from CharacterCreator.models import *

# def check_prereq(tree, c, prereq, prereq_level):
#     if prereq == 'none':
#         return True
#     else:
#         cskill = CharacterSkill.objects.filter(character=c, skill__name=prereq)
#         if cskill.current >= prereq_level:
#             return True
#         else:
#             return False


# roll all character statistics until their sum is "points"
def spend_stats(tree, c):

    cstats = CharacterStatistic.objects.filter(character=c).exclude(statistic__type=DEP).exclude(statistic__name='none')
    cpoints = CharacterPointpool.objects.filter(character=c)

    if len(cstats) == 0:
        return

    reject_names = []
    for i, cp in enumerate(cpoints):
        cp_in = False
        for cstat in cstats:
            if cstat.statistic.pointpool.name == cp.pointpool.name:
                cp_in = True
                break
        if not cp_in:
            reject_names.append(cp.pointpool.name)

    for reject in reject_names:
        cpoints = cpoints.exclude(pointpool__name=reject)

    for cp in cpoints:
        cx_not_all_max = True
        while cp.current > 0 and cx_not_all_max:
            cx_not_all_max = False
            weights = [cstat.current+1 for cstat in cstats]
            for cstat in cstats:
                if cstat.current < cstat.maximum and cstat.statistic.pointpool.name == cp.pointpool.name:
                    cx_not_all_max = True
                    break

            cstat = random.choices(cstats, weights=weights).pop()

            if cstat.statistic.pointpool.name == cp.pointpool.name:

                if cstat.statistic.direction == 'increasing' and cstat.current < cstat.maximum:
                    cost = cstat.statistic.cost * ( (cstat.current+1) ** cstat.statistic.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cstat.current += cstat.statistic.purchase
                        cstat.save()
                        cp.save()
                elif cstat.statistic.direction == 'decreasing' and cstat.current > cstat.minimum:
                    cost = cstat.statistic.cost * ( (cstat.maximum - cstat.current + 1) ** cstat.statistic.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cstat.current -= cstat.statistic.purchase
                        cstat.save()
                        cp.save()


# roll all character skills until their sum is "points"
def spend_skills(tree, c):

    cskills = CharacterSkill.objects.filter(character=c)
    cpoints = CharacterPointpool.objects.filter(character=c)

    if len(cskills) == 0:
        return

    reject_names = []
    for i, cp in enumerate(cpoints):
        cp_in = False
        for cskill in cskills:
            if cskill.skill.pointpool.name == cp.pointpool.name:
                cp_in = True
                break
        if not cp_in:
            reject_names.append(cp.pointpool.name)

    for reject in reject_names:
        cpoints = cpoints.exclude(pointpool__name=reject)

    for cp in cpoints:
        cx_not_all_max = True
        while cp.current > 0 and cx_not_all_max:
            cx_not_all_max = False
            weights = [cskill.current+1 for cskill in cskills]
            for cskill in cskills:
                if cskill.current < cskill.maximum and cskill.skill.pointpool.name == cp.pointpool.name:
                    cx_not_all_max = True
                    break

            cskill = random.choices(cskills, weights=weights).pop()
            unlocks = tree['skills'][cskill.skill.name]['unlocks']
            # rule for unlocking skills
            while cskill.current == cskill.maximum:
                if unlocks != 'none':
                    possibles = []
                    skill_threshes = unlocks.split(' OR ')
                    for skill_thresh in skill_threshes:
                        skill_name, thresh_string = skill_thresh.split('@')
                        skill_thresh = int(thresh_string)
                        # if statement to check the skill threshold
                        if cskill.current >= skill_thresh:
                            # if so, add it to the list of possible skill choices
                            possibles.append(skill_name)
                else:
                    break

                if len(possibles) > 0:
                    unlock_skills = CharacterSkill.objects.filter(character=c, name__in=possibles)
                else:
                    break

                cskill = random.choices(possibles, weights=[unlock_skill.current+1 for unlock_skill in unlock_skills]).pop()

            if cskill.skill.pointpool.name == cp.pointpool.name:

                if cskill.skill.direction == 'increasing' and cskill.current < cskill.maximum:
                    cost = cskill.skill.cost * ( (cskill.current+1) ** cskill.skill.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cskill.current += cskill.skill.purchase
                        cskill.save()
                        cp.save()
                elif cskill.skill.direction == 'decreasing' and cskill.current > cskill.minimum:
                    cost = cskill.skill.cost * ( (cskill.maximum - cskill.current + 1) ** cskill.skill.tier )
                    if cp.current >= cost:
                        cp.current -= cost
                        cskill.current -= cskill.skill.purchase
                        cskill.save()
                        cp.save()


# traits
def spend_traits(tree, c):

    traitcats = TraitCategory.objects.all().exclude(name='none')
    ctraits = CharacterTrait.objects.filter(character=c)
    cpoints = CharacterPointpool.objects.filter(character=c)

    if len(ctraits) == 0:
        return

    reject_names = []
    for i, cp in enumerate(cpoints):
        cp_in = False
        for ctrait in ctraits:
            if ctrait.trait.pointpool.name == cp.pointpool.name:
                cp_in = True
                break
        if not cp_in:
            reject_names.append(cp.pointpool.name)

    for reject in reject_names:
        cpoints = cpoints.exclude(pointpool__name=reject)

    for cp in cpoints:
        cx_not_all_max = True
        spent = cp.total
        while cp.current > 0 and cx_not_all_max and random.random() <= float(spent/cp.total):
            cx_not_all_max = False
            weights = [ctrait.current+1 for ctrait in ctraits]
            for ctrait in ctraits:
                if ctrait.current != ctrait.maximum:
                    cx_not_all_max = True
                    break

            traitcat = random.choice(traitcats)
            ctrait = random.choices(ctraits, weights=weights).pop()

            if ctrait.trait.pointpool.name == cp.pointpool.name and \
                ctrait.trait.category.name == traitcat.name:

                if ctrait.trait.direction == 'increasing' and ctrait.current < ctrait.maximum:
                    cost = ctrait.trait.cost * ( (ctrait.current+1) ** ctrait.trait.tier )
                    if cp.current >= cost:
                        spent -= abs(cost)
                        cp.current -= cost
                        ctrait.current += ctrait.trait.purchase
                        ctrait.save()
                        cp.save()
                elif ctrait.trait.direction == 'decreasing' and ctrait.current > ctrait.minimum:
                    cost = ctrait.trait.cost * ( (ctrait.maximum - ctrait.current + 1) ** ctrait.trait.tier )
                    if cp.current >= cost:
                        spent -= abs(cost)
                        cp.current -= cost
                        ctrait.current -= ctrait.trait.purchase
                        ctrait.save()
                        cp.save()

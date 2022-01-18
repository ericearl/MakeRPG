from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
# from django.views.generic import ListView
# from django.db.models import Q, Min, Max

from .models import *
from .forms import *

from urllib.parse import parse_qs
from urllib.parse import urlencode
import json

def character(request, character_id):
    character = Character.objects.get(pk=character_id)
    trait_list = CharacterTrait.objects.filter(character=character_id).order_by('trait__category__name')
    stat_list = CharacterStatistic.objects.filter(character=character_id).order_by('statistic__name')
    skill_list = CharacterSkill.objects.filter(character=character_id).order_by('skill__statistic__name', 'skill__name')
    point_list = CharacterPointpool.objects.filter(character=character_id).order_by('pointpool__name')
    history_list = CharacterEventRoll.objects.filter(character=character_id).order_by('pk')
    # npc_list = get_list_or_404(NPCEventRoll, character=character_id)
    # return render(request, 'CharacterCreator/character.html', {'character': character, 'stats': stat_list, 'skills': skill_list, 'points': point_list, 'history': history_list, 'npcs': npc_list })
    return render(request, 'CharacterCreator/character.html', {
            'character': character,
            'points': point_list,
            'stats': stat_list,
            'skills': skill_list,
            'traits': trait_list,
            'history': history_list
            })


def npc(request, npc_id):
    character = get_object_or_404(Character, pk=npc_id)
    stat_list = get_list_or_404(CharacterStatistic, character=npc_id)
    skill_list = get_list_or_404(CharacterSkill, character=npc_id)
    point_list = get_list_or_404(CharacterPointpool, character=npc_id)
    history_list = get_list_or_404(NPCEventRoll, npc=npc_id)
    return render(request, 'CharacterCreator/npc.html', {
        'character': character,
        'stats': stat_list,
        'skills': skill_list,
        'points': point_list,
        'history': history_list
        })


def redirect_params(url, param_dict=None):
    response = redirect(url)
    if param_dict:
        query_string = urlencode(param_dict)
        response['Location'] += '?' + query_string
    return response


def search(request):
    characters = Character.objects.exclude(name__contains='[NPC')
    point_list = Pointpool.objects.exclude(name='roll').order_by('name')
    stat_list = Statistic.objects.filter(name__in=['Body Save','Combat','Fear Save','Health','Intellect','Sanity Save','Speed','Strength']).order_by('name')
    skill_list = Skill.objects.filter(role__name='none').order_by('statistic__name', 'name')

    roleform = RoleForm()
    statforms = [StatisticForm(statistic=s.name) for s in stat_list]
    skillforms = [SkillForm(skill=s.name) for s in skill_list]

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        q = request.POST

        roles = q.getlist('role')
        mins = q.getlist('minimum')

        filters = {'statistic': {}, 'skill': {}}
        for s, m in zip(stat_list, mins[:len(stat_list)]):
            span = sorted(CharacterStatistic.objects.filter(statistic=s).values_list('current', flat=True).distinct())
            minimum = min(list(span))
            if int(m) > minimum:
                filters['statistic'][s.name] = int(m)
        for s, m in zip(skill_list, mins[len(stat_list):]):
            span = sorted(CharacterSkill.objects.filter(skill=s).values_list('current', flat=True).distinct())
            minimum = min(list(span))
            if int(m) > minimum:
                filters['skill'][s.name] = int(m)

        qs = urlencode(filters)
        parsed = parse_qs(qs)
        qs_filters = json.loads(parsed['statistic'][0].replace("'",'"'))

        # characters = characters.filter(role__in=roles)

        cstats = CharacterStatistic.objects.filter(character__role__in=roles)
        stat_filter = set([c.character.pk for c in cstats])
        for stat in filters['statistic']:
            minimum = filters['statistic'][stat]
            cstats = CharacterStatistic.objects.filter(character__role__in=roles, statistic__name=stat, current__gte=minimum)
            stat_filter = stat_filter & set([c.character.pk for c in cstats])

        cskills = CharacterSkill.objects.filter(character__role__in=roles)
        skill_filter = set([c.character.pk for c in cskills])
        for skill in filters['skill']:
            minimum = filters['skill'][skill]
            cskills = CharacterSkill.objects.filter(character__role__in=roles, skill__name=skill, current__gte=minimum)
            skill_filter = skill_filter & set([c.character.pk for c in cskills])

        pks = list(stat_filter & skill_filter)
        characters = characters.filter(pk__in=pks)

    character_list = characters.order_by('role', 'name')

    data = {
        'characters': character_list,
        'roleform': roleform,
        'statforms': statforms,
        'skillforms': skillforms,
        'stats': stat_list,
        'skills': skill_list,
        'points': point_list
        }

    # data = {
    #     'characters': character_list,
    #     'archetypeform': archetypeform,
    #     'roleform': roleform,
    #     'pointforms': pointforms,
    #     'statforms': statforms,
    #     'skillforms': skillforms,
    #     'stats': stat_list,
    #     'skills': skill_list,
    #     'points': point_list
    #     }

    return render(request, 'CharacterCreator/search.html', data)


def get_default_statistic(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StatisticForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            request.session.clear()
            for field in form.fields.keys():
                request.session['defstat' + field] = form.cleaned_data[field]
            return HttpResponseRedirect('/cc/statnames/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = StatisticForm(initial={'name': 'default'})

    return render(request, 'CharacterCreator/defaultstat.html', {'form': form})


def manage_statistic_names(request):
    if request.method == 'GET':
        formset = StatisticNameFormSet(request.GET or None)

    elif request.method == 'POST':
        formset = StatisticNameFormSet(request.POST)
        if formset.is_valid():
            for i,form in enumerate(formset):
                request.session['statname' + str(i)] = form.cleaned_data['name']
            return HttpResponseRedirect('/cc/statentry/')

    return render(request, 'CharacterCreator/manage_statistic_names.html', {'formset': formset})


def multi_statistic(request):
    if request.method == 'GET':
        initialdata = []
        for key in request.session.keys():
            if 'statname' in key and 'defstat' not in key:
                initdict = {}
                initdict['name'] = request.session[key]
                for field in ['minimum','maximum','direction','cost','tier']:
                    initdict[field] = request.session['defstat' + field]
                initialdata.append(initdict)

        formset = StatisticFormSet(request.GET or None, initial=initialdata)

    elif request.method == 'POST':
        formset = StatisticFormSet(request.POST)
        if formset.is_valid():
            return HttpResponseRedirect('/cc/statnames/')

    return render(request, 'CharacterCreator/multi_statistic.html', {'formset': formset})


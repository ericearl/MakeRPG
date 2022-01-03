from django import forms
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponseRedirect
from django.views.generic import ListView
# from django_tables2 import SingleTableView
from django.db.models import Q, Min, Max

from .models import *
from .forms import *


# class CharacterTableView(SingleTableView):
#     model = Character
#     table_class = CharacterTable
#     template_name = 'CharacterCreator/results.html'


def index(request):
    character_list = Character.objects.exclude(name__contains='[NPC').order_by('role__name', 'name')
    role_list = Role.objects.all().exclude(name='none').order_by('name')

    return render(request, 'CharacterCreator/index.html',
        {'character_list': character_list,
        'role_list': role_list}
        )


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


def search(request):
    characters = Character.objects.exclude(name__contains='[NPC')
    point_list = Pointpool.objects.exclude(name='roll').order_by('name')
    stat_list = Statistic.objects.filter(name__in=['Body Save','Combat','Fear Save','Health','Intellect','Sanity Save','Speed','Strength']).order_by('name')
    skill_list = Skill.objects.filter(role__name='none').order_by('statistic__name', 'name')

    roleform = RoleForm()

    statforms = [
        BodyStatForm(),
        CombatStatForm(),
        FearStatForm(),
        HealthStatForm(),
        IntellectStatForm(),
        SanityStatForm(),
        SpeedStatForm(),
        StrengthStatForm()
    ]

    # statforms = [StatisticForm() for s in stat_list]
    skillforms = [SkillForm() for s in skill_list]

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        q = request.POST

        roles = q.getlist('role')
        mins = q.getlist('minimum')

        characters = characters.filter(role__in=roles)
        for idx, val in enumerate(stat_list):
            check = CharacterStatistic.objects.filter(
                statistic__name=val.name,
                current__gte=mins[idx]
            )
            characters = characters.intersection(check)

        for idx, val in enumerate(skill_list):
            check = CharacterSkill.objects.filter(
                skill__name=val.name,
                current__gte=mins[idx+len(stat_list)]
            )

            characters = characters.intersection(check)

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


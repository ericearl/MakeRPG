# from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404, render
# from django.http import HttpResponse
# from django.template import loader
from .models import *


def index(request):
    npc_list = Character.objects.filter(name__contains='[NPC').order_by('role__name', 'name')
    npc_history_list = NPCEventRoll.objects.all()
    character_list = Character.objects.all().exclude(name__contains='[NPC').order_by('role__name', 'name')
    role_list = Role.objects.all().order_by('name')
    return render(request, 'CharacterCreator/index.html', {'character_list': character_list, 'npc_list': npc_list, 'npc_history': npc_history_list, 'role_list': role_list})


def character(request, character_id):
    character = get_object_or_404(Character, pk=character_id)
    stat_list = get_list_or_404(CharacterStatistic, character=character_id)
    skill_list = get_list_or_404(CharacterSkill, character=character_id)
    history_list = get_list_or_404(CharacterEventRoll, character=character_id)
    npc_list = get_list_or_404(NPCEventRoll, character=character_id)
    return render(request, 'CharacterCreator/character.html', {'character': character, 'stats': stat_list, 'skills': skill_list, 'history': history_list, 'npcs': npc_list })


def npc(request, npc_id):
    character = get_object_or_404(Character, pk=npc_id)
    stat_list = get_list_or_404(CharacterStatistic, character=npc_id)
    skill_list = get_list_or_404(CharacterSkill, character=npc_id)
    history_list = get_list_or_404(NPCEventRoll, npc=npc_id)
    return render(request, 'CharacterCreator/npc.html', {'character': character, 'stats': stat_list, 'skills': skill_list, 'history': history_list })


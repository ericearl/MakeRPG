import django_tables2 as tables
from django_tables2 import A
from .models import *

class CharacterTable(tables.Table):
    class Meta:
        # model = CharacterStatistic
        model = Character
        template_name = "django_tables2/bootstrap.html"
        # fields = ('character.name', 'character.role', 'statistic', 'current')
        fields = ('role', 'name')

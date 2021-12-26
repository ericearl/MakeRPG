from django import forms
from django.db.models import Min, Max
from .models import *


# class BaseStatisticNameFormSet(forms.BaseFormSet):
#     def add_fields(self, form, index):
#         super().add_fields(form, index)
#         form.fields["name"] = forms.CharField()


# class PointForm(forms.Form):
#     def __init__(self, bottom, top, *args, **kwargs):
#         self.bottom = bottom
#         self.top = top
#         self.span = [x for x in range(bottom, top+1)]

#         self.field = forms.TypedChoiceField(
#                 choices = zip(self.span, self.span),
#                 coerce = int,
#                 empty_value = self.bottom
#                 )

#         super(PointForm, self).__init__(*args, **kwargs)


# class ActiveSkillPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Active Skill').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Active Skill').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Active Skill').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class AttributePointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Attribute').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Attribute').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Attribute').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class ComplexFormPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Complex Form').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Complex Form').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Complex Form').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class KarmaPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Karma').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Karma').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Karma').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class MagicalSkillPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Magical Skill').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Magical Skill').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Magical Skill').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class MagicalSkillGroupPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Magical Skill Group').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Magical Skill Group').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Magical Skill Group').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class NuyenPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Nuyen').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Nuyen').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Nuyen').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class ResonanceSkillPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Resonance Skill').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Resonance Skill').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Resonance Skill').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


class SkillPointForm(forms.Form):
    span = sorted(CharacterPointpool.objects.filter(pointpool__name='Skill').values_list('current', flat=True).distinct())
    # bottom = CharacterPointpool.objects.filter(pointpool__name='Skill').aggregate(Min('current'))
    # top = CharacterPointpool.objects.filter(pointpool__name='Skill').aggregate(Max('total'))
    # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

    minimum = forms.TypedChoiceField(
            choices = zip(span, span),
            coerce = int,
            empty_value = min(list(span))
            )


# class SkillGroupPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Skill Group').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Skill Group').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Skill Group').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class SpecialAttributePointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Special Attribute').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Special Attribute').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Special Attribute').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class SpellPointForm(forms.Form):
#     span = sorted(CharacterPointpool.objects.filter(pointpool__name='Spell').values_list('current', flat=True).distinct())
#     # bottom = CharacterPointpool.objects.filter(pointpool__name='Spell').aggregate(Min('current'))
#     # top = CharacterPointpool.objects.filter(pointpool__name='Spell').aggregate(Max('total'))
#     # span = [x for x in range(bottom['current__min'], top['total__max']+1)]

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class AGILITYStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='AGILITY').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class BODYStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='BODY').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class CHARISMAStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='CHARISMA').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class EDGEStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='EDGE').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class ESSENCEStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='ESSENCE').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class INTUITIONStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='INTUITION').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class LOGICStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='LOGIC').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class REACTIONStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='REACTION').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class RESONANCEStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='RESONANCE').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class STRENGTHStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='STRENGTH').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


# class WILLPOWERStatForm(forms.Form):
#     span = sorted(CharacterStatistic.objects.filter(statistic__name='WILLPOWER').values_list('current', flat=True).distinct())

#     minimum = forms.TypedChoiceField(
#             choices = zip(span, span),
#             coerce = int,
#             empty_value = min(list(span))
#             )


class SkillForm(forms.Form):
    span = sorted(CharacterSkill.objects.all().values_list('current', flat=True).distinct())

    minimum = forms.TypedChoiceField(
        choices = zip(span, span),
        coerce = int,
        empty_value = min(list(span))
        )


class RoleForm(forms.Form):
    roles = Role.objects.exclude(name='none')
    role = forms.ModelMultipleChoiceField(
        queryset = roles
        )

# class ArchetypeForm(forms.Form):
#     archetypes = Archetype.objects.exclude(name='none')
#     archetype = forms.ModelMultipleChoiceField(
#         queryset = archetypes
#         )

class StatisticNameForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'label': 'Name:',
            'class': 'form-control'
            })
        )


class StatisticForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(StatisticForm, self).__init__(*args, **kwargs)
    #     if 'name' in kwargs:
    #         self.fields['name'] = kwargs['name']

    class Meta:
        model = Statistic
        fields = '__all__'


StatisticNameFormSet = forms.formset_factory(StatisticNameForm)
StatisticFormSet = forms.formset_factory(StatisticForm, extra=0)
# PointFormSet = forms.formset_factory(PointForm, extra=11)
# TypedChoiceFieldSet = forms.formset_factory(forms.TypedChoiceField, extra=11)

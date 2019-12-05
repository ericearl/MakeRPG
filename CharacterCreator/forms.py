from django import forms
from django.db.models import Min, Max
from .models import *


# class BaseStatisticNameFormSet(forms.BaseFormSet):
#     def add_fields(self, form, index):
#         super().add_fields(form, index)
#         form.fields["name"] = forms.CharField()


class PointForm(forms.Form):
    bottom = 0
    top = 90
    span = range(bottom,top+1)

    minimum = forms.TypedChoiceField(
        choices = zip(span, span),
        coerce = int,
        empty_value = bottom
        )

class StatForm(forms.Form):
    bottom = 1
    top = 10
    span = range(bottom,top+1)

    minimum = forms.TypedChoiceField(
        choices = zip(span, span),
        coerce = int,
        empty_value = bottom
        )

class SkillForm(forms.Form):
    bottom = 0
    top = 10
    span = range(bottom,top+1)

    minimum = forms.TypedChoiceField(
        choices = zip(span, span),
        coerce = int,
        empty_value = bottom
        )


class RoleForm(forms.Form):
    roles = Role.objects.exclude(name='none')
    role = forms.ModelMultipleChoiceField(
        queryset = roles
        )

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
PointFormSet = forms.formset_factory(PointForm)

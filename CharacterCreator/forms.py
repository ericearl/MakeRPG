from django import forms
from .models import *


# class BaseStatisticNameFormSet(forms.BaseFormSet):
#     def add_fields(self, form, index):
#         super().add_fields(form, index)
#         form.fields["name"] = forms.CharField()


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


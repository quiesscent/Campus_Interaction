from django import forms
from django.forms import formset_factory
from .models import Poll, Option

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'description', 'poll_type']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_text']

OptionFormSet = formset_factory(OptionForm, extra=1)

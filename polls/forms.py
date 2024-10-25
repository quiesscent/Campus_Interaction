from django import forms
from django.forms import modelformset_factory
from .models import Poll, Option

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = [
            'title', 'description', 'poll_type', 'expiration_time', 'allow_expiration',
            'background_color', 'show_share_button', 'poll_language', 'is_public', 
            'banner_image', 'multi_option'  # Added `multi_option` field
        ]
        widgets = {
            'expiration_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'poll_type': forms.Select(attrs={'class': 'form-select'}),
            'banner_image': forms.ClearableFileInput(),
            'allow_expiration': forms.CheckboxInput(),
            'multi_option': forms.CheckboxInput(),  # Checkbox for multi-option
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_text', 'is_correct']

OptionFormSet = modelformset_factory(Option, form=OptionForm, extra=1)

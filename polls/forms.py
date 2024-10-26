from django import forms
from django.forms import modelformset_factory
from .models import Poll, Option

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = [
            'title', 'description', 'poll_type', 'expiration_time', 'allow_expiration',
            'background_color', 'show_share_button', 'is_public', 
            'banner_image', 'multi_option'  
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-title', 'placeholder': 'Enter poll title'}),
            'description': forms.Textarea(attrs={
                'class': 'form-description',
                'id': 'id_description',
                'placeholder': 'Enter poll description (optional)'  # Optional placeholder
            }),
            'expiration_time': forms.DateTimeInput(attrs={'class': 'form-period', 'type': 'datetime-local'}),
            'background_color': forms.TextInput(attrs={'class': 'form-image', 'type': 'color', 'id': 'background-color-picker',}),
            'poll_type': forms.Select(attrs={'class': 'form-option'}),
            'banner_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'allow_expiration': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'multi_option': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_share_button': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['option_text', 'is_correct']

        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-option-text', 'placeholder': 'Enter option text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Call the parent constructor
        if self.instance and self.instance.pk:
            self.fields['option_text'].required = False  # Make option_text optional for existing options

OptionFormSet = modelformset_factory(Option, form=OptionForm, extra=2)

# If you want new options to be required, do not set required = False in the init method above

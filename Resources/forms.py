from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Resource, Comment

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 
                 'phone_number', 'bio', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class ResourceUploadForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'category', 'resource_type', 
                 'file', 'external_link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'resource_type': forms.Select(choices=Resource.RESOURCE_TYPES)
        }
        
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        external_link = cleaned_data.get('external_link')
        resource_type = cleaned_data.get('resource_type')
        
        if not file and not external_link:
            raise forms.ValidationError(
                "You must provide either a file or an external link."
            )
            
        # Validate that file is provided for certain resource types
        if resource_type in ['DOC', 'PDF'] and not file:
            raise forms.ValidationError(
                f"A file upload is required for {dict(Resource.RESOURCE_TYPES)[resource_type]} resources."
            )
            
        # Validate that external link is provided for Link type
        if resource_type == 'LNK' and not external_link:
            raise forms.ValidationError(
                "An external link is required for Link resources."
            )
        
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment here...'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].label = "Comment"
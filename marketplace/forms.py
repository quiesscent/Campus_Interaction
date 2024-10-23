from django import forms
from .models import Item, UserRating

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'category', 'image']

class RatingForm(forms.ModelForm):
    class Meta:
        model = UserRating
        fields = ['stars', 'comment']



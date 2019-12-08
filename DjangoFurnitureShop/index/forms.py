from django import forms
from .models import Product, Comment

class ProductForm(forms.ModelForm):
    # name = forms.CharField(max_length=200)
    # description = forms.CharField(max_length=200)
    # price = forms.FloatField()
    # photo = forms.ImageField(required=False, max_length=255)

    class Meta:
        model = Product
        fields = ('name', 'manufacturer', 'description', 'price', 'photo')

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text')


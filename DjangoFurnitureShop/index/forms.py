from django import forms
from .models import Product, Comment, UserAddress
import django_filters


class ProductForm(forms.ModelForm):
    name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=200)
    price = forms.FloatField()
    photo = forms.ImageField(required=False, max_length=255)

    class Meta:
        model = Product
        fields = ('name', 'manufacturer', 'description', 'price', 'photo')

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text')

class CheckoutForm(forms.Form):
    company_name = forms.CharField(max_length=20)
    name = forms.CharField(max_length=30)
    surname = forms.CharField(max_length=30)
    street = forms.CharField(max_length=30)
    house_number = forms.CharField(max_length=30)
    house_unit_number = forms.CharField(max_length=30)
    post_code = forms.CharField(max_length=30)
    city = forms.CharField(max_length=30)
    
    class Meta:
        model = UserAddress
        fields = ('author', 'text')
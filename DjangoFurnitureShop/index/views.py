from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Product, Comment
from .forms import ProductForm, CommentForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


# def product_list(request):
#     products = Product.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
#     users = User.objects.all()
#     return render(request, 'index/product_list.html', {'products': products, 'users': users})


# @login_required
# def product_new(request):
#     if request.method == "product":
#         form = ProductForm(request.product)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.author = request.user
#             product.published_date = timezone.now()
#             product.save()
#             return redirect('product_detail', pk=product.pk)
#     else:
#         form = ProductForm()
#     return render(request, 'index/product_edit.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    users = User.objects.all()
    return render(request, 'index/product_list.html', {'products': products, 'users': users})

def a_product_list(request, pk):
	products = Product.objects.filter(manufacturer=pk)
	return render(request, 'index/a_product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'index/product_detail.html', {'product': product})

def new_product(request):
    if request.method == "POST":
        product = ProductForm(request.POST, request.FILES)
        if product.is_valid():
            product.save()
            return redirect('/')
    else:
        product = ProductForm()
    return render(request, 'index/new_product.html', {'product': product})

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    users = User.objects.all()
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.manufacturer = request.user
            product.created_date = timezone.now()
            product.save()
            return redirect('product_details', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'index/edit_product.html', {'product': product, 'users': users})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('/')

# Create your views here.

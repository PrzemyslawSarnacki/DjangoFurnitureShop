from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from .models import Product, Comment
from .forms import ProductForm, CommentForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


def product_list(request):
    search_phrase = ''
    search_manufacturer = ''
    products = Product.objects.all() 
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    users = User.objects.all()
    if 'search' in request.GET:
        search_phrase = request.GET['search']
        products = products.filter(manufacturer_id__username=search_phrase)
        print(products.first())
        if products.first() == None:
            products = Product.objects.all()
            products = products.filter(name__icontains=search_phrase)
            print(products) 
    if 'search_manufacturer' in request.GET:
        search_manufacturer = request.GET['search_manufacturer']
        products = products.filter(manufacturer_id__username=search_manufacturer)
    context = {'products': products, 'users': users, 'search_phrase': search_phrase, 'search_manufacturer': search_manufacturer}
    return render(request, 'index/product_list.html', context)

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
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.manufacturer = request.user
            product.created_date = timezone.now()
            product.save()
            return redirect('product_details', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'index/edit_product.html', {'form': form})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('/')

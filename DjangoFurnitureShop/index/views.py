from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Product, Comment
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
# Create your views here.

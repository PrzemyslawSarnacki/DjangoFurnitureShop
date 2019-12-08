from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Product, Comment
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters


# def product_list(request):
#     products = Product.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
#     users = User.objects.all()
#     return render(request, 'index/product_list.html', {'products': products, 'users': users})

# def a_post_list(request, pk):
# 	products = Product.objects.filter(author=pk)
# 	return render(request, 'index/a_product_list.html', {'products': products})

# @login_required
# def post_new(request):
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             product = form.save(commit=False)
#             product.author = request.user
#             product.published_date = timezone.now()
#             product.save()
#             return redirect('product_detail', pk=product.pk)
#     else:
#         form = ProductForm()
#     return render(request, 'index/product_edit.html', {'form': form})

def index(request):
    products = Product.objects.all()
    users = User.objects.all()
    return render(request, 'index/product_list.html', {'products': products, 'users': users})

# Create your views here.

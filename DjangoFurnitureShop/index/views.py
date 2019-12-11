from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from .models import Product, Comment, Order, OrderProduct, UserAddress
from .forms import ProductForm, CommentForm, CheckoutForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail, EmailMessage
from . import generate_invoice


def product_list(request):
    search_phrase = ''
    search_manufacturer = ''
    products = Product.objects.all()
    users = User.objects.all()
    if 'search' in request.GET:
        products = Product.objects.all()
        search_phrase = request.GET['search']
        products = products.filter(manufacturer_id__username=search_phrase)
        if products.first() == None:
            products = Product.objects.all()
            products = products.filter(name__icontains=search_phrase)
    if 'search_manufacturer' in request.GET:
        products = Product.objects.all()
        search_manufacturer = request.GET['search_manufacturer']
        products = products.filter(
            manufacturer_id__username=search_manufacturer)
    else:
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        products = paginator.get_page(page)
    context = {'products': products, 'users': users,
               'search_phrase': search_phrase, 'search_manufacturer': search_manufacturer}
    return render(request, 'index/product_list.html', context)


def a_product_list(request, pk):
    products = Product.objects.filter(manufacturer=pk)
    return render(request, 'index/a_product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'index/product_detail.html', {'product': product})


def new_product(request):
    if request.method == 'POST':
        product = ProductForm(request.POST, request.FILES)
        if product.is_valid():
            product.save()
            return redirect('/')
    else:
        product = ProductForm()
    return render(request, 'index/new_product.html', {'product': product})


def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.manufacturer = request.user
            product.created_date = timezone.now()
            product.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'index/edit_product.html', {'form': form})


def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return render(request, 'index/delete_product.html', {'product': product})


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        order_product = OrderProduct.objects.get(
            product=product, user=request.user, ordered=False)
    except ObjectDoesNotExist:
        order_product = OrderProduct.objects.create(
            product=product, user=request.user, ordered=False)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        if order.products.filter(product__pk=product.pk).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, "Zaaktualizowano ilość.")
            return redirect("order_summary")
        else:
            order.products.add(order_product)
            messages.info(request, "Dodano do koszyka.")
            return redirect("order_summary")
    except ObjectDoesNotExist:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.products.add(order_product)
        messages.info(request, "Dodano do koszyka.")
        return(redirect('order_summary'))


def order_summary(request):
    if request.method == "GET":
        try:
            order = Order.objects.get(user=request.user, ordered=False)

            return render(request, 'index/order_summary.html', {'order': order})
        except ObjectDoesNotExist:
            messages.warning(request, "Nie masz aktywnego zamówienia !")
            return redirect("/")


def checkout(request):
    if request.method == "GET":
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            shipping_address_qs = UserAddress.objects.filter(
                user=request.user,
            )
            if shipping_address_qs.exists():
                form = CheckoutForm(initial={
                    'company_name': shipping_address_qs[0].company_name,
                    'name': shipping_address_qs[0].name,
                    'surname': shipping_address_qs[0].surname,
                    'street': shipping_address_qs[0].street,
                    'house_number': shipping_address_qs[0].house_number,
                    'house_unit_number': shipping_address_qs[0].house_unit_number,
                    'post_code': shipping_address_qs[0].post_code,
                    'city': shipping_address_qs[0].city
                })
            else:
                form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }
            return render(request, "index/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(request, "Nie masz żadnego zamówienia")
            return redirect('/')
    if request.method == "POST":
        form = CheckoutForm(data=request.POST)
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            if form.is_valid():
                company_name = form.cleaned_data.get('company_name')

                name = form.cleaned_data.get('name')
                surname = form.cleaned_data.get('surname')
                street = form.cleaned_data.get('street')
                house_number = form.cleaned_data.get('house_number')
                house_unit_number = form.cleaned_data.get('house_unit_number')
                post_code = form.cleaned_data.get('post_code')
                city = form.cleaned_data.get('city')
                payment_deadline = form.cleaned_data.get('payment_deadline')

                shipping_address = UserAddress(
                    user=request.user,
                    company_name=company_name,
                    name=name,
                    surname=surname,
                    street=street,
                    house_number=house_number,
                    house_unit_number=house_unit_number,
                    post_code=post_code,
                    city=city
                )
                shipping_address.save()
                order_products = OrderProduct.objects.filter(
                    user=request.user, ordered=False
                )
                items_list = []
                for order_product in order_products:
                    order_product.ordered = True
                    order_product.save()
                    items_list.append(order_product.quantity)
                    items_list.append(order_product.product.price)
                    items_list.append(order_product.product.name)
                generate_invoice.create_invoice('Meble Warszawa', 'ul. Warszawska 21', '00-000 Warszawa',
                                                f'{shipping_address.name} {shipping_address.surname}',
                                                f'{shipping_address.street} {shipping_address.house_number}',
                                                shipping_address.post_code, items_list)
                order.shipping_address = shipping_address
                order.ordered = True
                order.payment_deadline = payment_deadline

                email = EmailMessage('Potwierdzenie zamówienia',
                                     f''' To jest wiadomość wygenerowana automatycznie.
                    NIE ODPOWIADAJ NA OTRZYMANĄ WIADOMOŚĆ.

                    Dziękujemy za złożenie zamówienia.
                    Wartość zamówienia wynosi {order.get_total()} zł.
                    Należność należy wpłacić do dnia : {payment_deadline}
                    W przeciwnym razie zamówienie zostanie anulowane.
                    ''', 'dawid.laskowski97@gmail.com', ['przemos100@gmail.com'])
                email.attach_file('Proforma.pdf')
                email.send()

                order.save()
                return render(request, "index/order_complete.html", {})
            else:
                print(form.errors)
                messages.info(
                    request, "Wypełnij wymagane pola")
                return redirect("checkout")

        except ObjectDoesNotExist:
            messages.warning(
                request, "Nie posiadasz żadnego aktywnego zamówienia")
            return redirect("order_summary")


def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        try:
            order_product = OrderProduct.objects.get(
                product=product, user=request.user, ordered=False)
            order.products.remove(order_product)
            messages.info(request, 'Produkt usunięty z koszyka')
            return redirect('order_summary')
        except ObjectDoesNotExist:
            messages.info(request, 'Koszyk jest pusty')
            return redirect('product_detail', pk=pk)
    except ObjectDoesNotExist:
        messages.info(request, 'Koszyk jest pusty')
        return redirect('product_detail', pk=pk)


def remove_single_product_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        order = Order.objects.get(
            user=request.user,
            ordered=False
        )
        if order.products.filter(product__pk=product.pk).exists():
            order_product = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order_product.save()
            else:
                order.products.remove(order_product)
            messages.info(request, 'Zaktualizowano ilość.')
            return redirect('order_summary')
        else:
            messages.info(request, 'Nie ma tego produktu w koszyku')
            return redirect('product_detail', pk=pk)
    except ObjectDoesNotExist:
        messages.info(request, 'Nie masz żadnego zamówienia')
        return redirect('product_detail', pk=pk)

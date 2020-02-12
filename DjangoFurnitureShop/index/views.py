from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Product, Comment, Order, OrderProduct, UserAddress
from .forms import ProductForm, CommentForm, CheckoutForm
from django.core.mail import EmailMessage
from . import generate_invoice
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View


class ProductListView(ListView):
    model = Product
    paginate_by = 3

    def get_queryset(self):
        search_phrase = self.request.GET.get('search')
        # search_manufacturer = self.request.GET.get('search_manufacturer')
        if search_phrase == None:
            search_phrase = self.request.GET.get('search_manufacturer')
            if search_phrase == None:
                object_list = self.model.objects.all()
            elif search_phrase != '':
                object_list = self.model.objects.filter(
                    manufacturer_id__username__icontains=search_phrase)
            else:
                object_list = self.model.objects.all()
        elif search_phrase != '':
            object_list = self.model.objects.filter(
                name__icontains=search_phrase)
        else:
            object_list = self.model.objects.all()
        return object_list


class ProductDetailView(DetailView):
    model = Product


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'index/new_product.html'
    fields = ['name', 'description', 'price', 'photo']

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.manufacturer = self.request.user
        obj.save()
        return redirect('/')


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'index/edit_product.html'
    fields = ['name', 'description', 'price', 'photo']


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product_list')


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = OrderProduct.objects.filter(user=self.request.user, ordered=False)
            for o in order:
                print(o.quantity)

            return render(self.request, 'index/cart.html', {'order': order})
        except ObjectDoesNotExist:
            messages.warning(self.request, "Nie masz aktywnego zamówienia !")
            return redirect("/")


class CheckoutView(View, LoginRequiredMixin):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            shipping_address_qs = UserAddress.objects.filter(
                user=self.request.user,
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
            return render(self.request, "index/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Nie masz żadnego zamówienia")
            return redirect('/')

    def post(self, *args, **kwargs):
        form = CheckoutForm(data=self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
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
                    user=self.request.user,
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
                    user=self.request.user, ordered=False
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
                    ''', 'dawid.laskowski97@gmail.com', [str(self.request.user.email)])
                email.attach_file('Proforma.pdf')
                email.send()

                order.save()
                return render(self.request, "index/order_complete.html", {})
            else:
                print(form.errors)
                messages.info(
                    self.request, "Wypełnij wymagane pola")
                return redirect("checkout")

        except ObjectDoesNotExist:
            messages.warning(
                self.request, "Nie posiadasz żadnego aktywnego zamówienia")
            return redirect("cart")

@login_required
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
            return redirect("cart")
        else:
            order.products.add(order_product)
            messages.info(request, "Dodano do koszyka.")
            return redirect("cart")
    except ObjectDoesNotExist:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.products.add(order_product)
        messages.info(request, "Dodano do koszyka.")
        return(redirect('cart'))

@login_required
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        try:
            order_product = OrderProduct.objects.get(
                product=product, user=request.user, ordered=False)
            order.products.remove(order_product)
            messages.info(request, 'Produkt usunięty z koszyka')
            return redirect('cart')
        except ObjectDoesNotExist:
            messages.info(request, 'Koszyk jest pusty')
            return redirect('product_detail', pk=pk)
    except ObjectDoesNotExist:
        messages.info(request, 'Koszyk jest pusty')
        return redirect('product_detail', pk=pk)

@login_required
def remove_single_product_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        order = Order.objects.get(
            user=request.user,
            ordered=False
        )
        if order.products.filter(product__pk=product.pk).exists():
            order_product = OrderProduct.objects.filter(
                user=request.user,
                ordered=False
            )[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order_product.save()
            else:
                order.products.remove(order_product)
            messages.info(request, 'Zaktualizowano ilość.')
            return redirect('cart')
        else:
            messages.info(request, 'Nie ma tego produktu w koszyku')
            return redirect('product_detail', pk=pk)
    except ObjectDoesNotExist:
        messages.info(request, 'Nie masz żadnego zamówienia')
        return redirect('product_detail', pk=pk)

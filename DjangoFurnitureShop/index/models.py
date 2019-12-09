from django.conf import settings 
from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=200)
    # manufacturer = models.CharField(max_length=200)
    manufacturer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)
    price = models.FloatField()
    photo = models.ImageField(upload_to = 'media/', max_length=255, null=True, blank=True)

    def create(self):
        self.created_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name


class Comment(models.Model):
	post = models.ForeignKey('index.Product', on_delete=models.CASCADE, related_name='comments')
	author = models.CharField(max_length=200)
	text = models.TextField()
	created_date = models.DateTimeField(default=timezone.now)
	approved_comment = models.BooleanField(default=False)

	def approve(self):
		self.approved_comment = True
		self.save()


	def __str__(self):
		return self.text


class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price



class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    # list_of_products = models.DictWrapper(products_dictionary)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'UserAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    sale_date = models.DateField(auto_now_add=True)
    payment_deadline = models.DateField()
    # total_price = models.FloatField()


class User(models.Model):
    login = models.CharField(max_length=10)
    password = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)


class UserAddress(models.Model):
    username = models.CharField(max_length=10)
    company_name = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    house_number = models.CharField(max_length=30)
    house_unit_number = models.CharField(max_length=30)
    post_code = models.CharField(max_length=30)
    city = models.CharField(max_length=30)


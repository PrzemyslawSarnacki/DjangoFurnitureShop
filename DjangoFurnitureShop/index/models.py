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



class Order(models.Model):
    client = models.CharField(max_length=200)
    products_dictionary = { 
        "product" : "",
        "price" : ""
    }
    # list_of_products = models.DictWrapper(products_dictionary)
    sale_date = models.DateField() 
    payment_deadline = models.DateField()
    total_price = models.FloatField()


class User(models.Model):
    login = models.CharField(max_length=10)
    password = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    email = models.CharField(max_length=30)


class User_Address(models.Model):
    username = models.CharField(max_length=10)
    company_name = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    house_number = models.CharField(max_length=30)
    house_unit_number = models.CharField(max_length=30)
    post_code = models.CharField(max_length=30)
    city = models.CharField(max_length=30)

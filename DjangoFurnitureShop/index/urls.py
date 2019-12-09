from django.urls import path, re_path
from django.conf.urls import url

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product_detail/<pk>/', views.product_detail, name='product_detail'),
    # re_path(r'^search/$', views.search, name='search'),
    path('new_product/', views.new_product, name='new_product'),
    path('edit_product/<pk>/', views.edit_product, name='edit_product'),
    path('delete_product/<pk>/', views.delete_product, name='delete_product'),
    path('<int:id>', views.product_list, name=''),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Create your tests here.  
 
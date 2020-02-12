from django.urls import path, re_path
from django.conf.urls import url

from . import views
from .views import ProductListView, ProductDetailView, ProductCreateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('', views.product_list, name='product_list'),
    path('', ProductListView.as_view(), name='product_list'),
    path('product_detail/<pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('new_product/', ProductCreateView.as_view(), name='new_product'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_summary/', views.order_summary, name='order_summary'),
    path('edit_product/<pk>/', views.edit_product, name='edit_product'),
    path('add_to_cart/<pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_single_product_from_cart/<pk>/', views.remove_single_product_from_cart,
         name='remove_single_product_from_cart'),
    path('product_detail/<pk>/delete_product/', views.delete_product, name='delete_product'),
    path('email/', views.checkout, name='email'),
    # path('<int:id>', views.product_list, name=''),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Create your tests here.  
 
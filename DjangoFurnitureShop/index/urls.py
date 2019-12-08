from django.urls import path
from django.conf.urls import url

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product_detail/<pk>/', views.product_detail, name='product_detail'),
    path('<int:id>', views.product_list, name=''),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Create your tests here.  
 
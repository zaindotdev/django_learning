from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path("products/info/", views.product_info, name='product_info'),
    path('orders/', views.order_list, name='order_list'),
]

from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
urlpatterns = [
    # path("products/create/", views.CreateProduct.as_view(), name='create_product'),
    # path('products/', views.ProductList.as_view(), name='product_list'),
    path('products/', views.ProductListCreateView.as_view(), name='product_list_create'),
    path('products/<int:product_id>/', views.ProductDetail.as_view(), name='product_detail'),
    path("products/info/", views.ProductInfo.as_view(), name='product_info'),
    # path('orders/', views.OrderList.as_view(), name='order_list'),
    # path('user-orders/', views.UserOrderList.as_view(), name='user_orders')
]
router = DefaultRouter()

router.register('orders', views.OrderViewSet)
urlpatterns += router.urls
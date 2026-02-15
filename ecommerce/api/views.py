# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
from django.db.models import Max
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response

# from rest_framework.decorators import api_view
from rest_framework.views import APIView

from api.filters import InStockFilterBackend, OrderFilter, ProductFilter
from api.models import Order, Product, User
from api.serializers import OrderSerializer, ProductInfoSerializer, ProductSerializer, OrderCreateSerializer, UserSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from api.tasks import send_order_confirmation_email

# @api_view(['GET'])
# def product_list(request):
#   products = Product.objects.all()
#   serializer = ProductSerializer(products, many=True)

#   return Response(serializer.data, status=200)

# class ProductList(generics.ListAPIView):
#   queryset = Product.objects.filter(stock__gt=0)
#   serializer_class = ProductSer ializer


class ProductListCreateView(generics.ListCreateAPIView):
    throttle_scope = 'products'
    queryset = Product.objects.order_by("pk")
    serializer_class = ProductSerializer
    # filterset_fields = ('name', 'price')
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    # you can use = sign to show the exact match results
    search_fields = ["=name", "description"]
    ordering_fields = ["name", "price", "stock"]
    pagination_class = LimitOffsetPagination
    pagination_class.page_size = 4
    # pagination_class.page_query_param = 'page_number'
    # pagination_class.page_size_query_param = 'page_size'
    # pagination_class.max_page_size = 10
    pagination_class.default_limit = 10
    pagination_class.offset_query_param = "offset"
    pagination_class.max_limit = 20
    pagination_class.offset_query_description = "Number of items to skip"

    @method_decorator(cache_page(60 * 5, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()
    

    def get_permissions(self):
        self.permission_classes = [permissions.AllowAny]
        if self.request.method == "POST":
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    # def create(self, request, *args, **kwargs):
    #   print(request.data)
    #   return super().create(request, *args, **kwargs)


# @api_view(['GET'])
# def product_detail(request, pk):
#   product = get_object_or_404(Product, pk=pk)
#   serializer = ProductSerializer(
#       product)

#   return Response(serializer.data, status=200)


# class ProductDetail(generics.RetrieveAPIView):
#   queryset = Product.objects.all()
#   serializer_class = ProductSerializer
#   lookup_url_kwarg = 'product_id'


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = "product_id"

    def get_permissions(self):
        self.permission_classes = [permissions.AllowAny]
        if self.request.method == "PUT" or self.request.method == "DELETE":
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()


# @api_view(['GET'])
# def order_list(request):
#   orders = Order.objects.prefetch_related('items__product')
#   serializer = OrderSerializer(orders, many=True)

#   return Response(serializer.data, status=200)

# class OrderList(generics.ListAPIView):
#   queryset = Order.objects.prefetch_related('items__product')
#   serializer_class = OrderSerializer


# class UserOrderList(generics.ListAPIView):
#   queryset = Order.objects.prefetch_related('items__product')
#   serializer_class = OrderSerializer
#   permission_classes = [permissions.IsAuthenticated]


#   # can help with dynamic filtering
#   def get_queryset(self):
#     # user = self.request.user
#     qs = super().get_queryset()
#     return qs.filter(user=self.request.user)

# # @api_view(['GET'])
# # def product_info(request):
# #   products = Product.objects.all()
# #   serializer = ProductInfoSerializer({
# #     'products':products,
# #     'count':len(products),
# #     'max_price': products.aggregate(max_price = Max('price'))['max_price']
# #   })

# #   return Response(serializer.data, status=200)


class ProductInfo(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer(
            {
                "products": products,
                "count": len(products),
                "max_price": products.aggregate(max_price=Max("price"))["max_price"],
            }
        )

        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    throttle_scope = "orders"
    queryset = Order.objects.prefetch_related("items__product")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @method_decorator(cache_page(60 * 5, key_prefix="product_list"))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        
        if order is not None:
            send_order_confirmation_email.delay(order.order_id, self.request.user.email)

    def get_serializer_class(self):
        #  can use if self.request.method == "POST":
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    # Redundant Code
    # @action(
    #     detail=False,
    #     methods=["get"],
    #     url_path="user-orders",
    #     permission_classes=[permissions.IsAuthenticated],
    # )
    # def user_orders(self, request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     seriaizer = self.get_serializer(orders, many=True)
    #     return Response(seriaizer.data)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None

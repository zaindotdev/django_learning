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
from api.models import Order, Product
from api.serializers import OrderSerializer, ProductInfoSerializer, ProductSerializer, OrderCreateSerializer

# @api_view(['GET'])
# def product_list(request):
#   products = Product.objects.all()
#   serializer = ProductSerializer(products, many=True)

#   return Response(serializer.data, status=200)

# class ProductList(generics.ListAPIView):
#   queryset = Product.objects.filter(stock__gt=0)
#   serializer_class = ProductSer ializer


class ProductListCreateView(generics.ListCreateAPIView):
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
    queryset = Order.objects.prefetch_related("items__product")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        #  can use if self.request.method == "POST":
        if self.action == 'create':
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

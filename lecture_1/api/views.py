# from django.http import JsonResponse
from api.serializers import ProductSerializer, OrderSerializer, ProductInfoSerializer
from api.models import Product, Order
from rest_framework.response import Response
# from rest_framework.decorators import api_view
from rest_framework.views import APIView
# from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework import generics, permissions 
 
# @api_view(['GET'])
# def product_list(request):
#   products = Product.objects.all()
#   serializer = ProductSerializer(products, many=True)
  
#   return Response(serializer.data, status=200)

# class ProductList(generics.ListAPIView):
#   queryset = Product.objects.filter(stock__gt=0)
#   serializer_class = ProductSerializer

class ProductListCreateView(generics.ListCreateAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer

class CreateProduct(generics.CreateAPIView):
  model = Product
  serializer_class = ProductSerializer

  # def create(self, request, *args, **kwargs):
  #   print(request.data)
  #   return super().create(request, *args, **kwargs)  

# @api_view(['GET'])
# def product_detail(request, pk):
#   product = get_object_or_404(Product, pk=pk)
#   serializer = ProductSerializer(
#       product)

#   return Response(serializer.data, status=200)


class ProductDetail(generics.RetrieveAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
  lookup_url_kwarg = 'product_id'
  
  
# @api_view(['GET'])
# def order_list(request):
#   orders = Order.objects.prefetch_related('items__product')
#   serializer = OrderSerializer(orders, many=True)

#   return Response(serializer.data, status=200)

class OrderList(generics.ListAPIView):
  queryset = Order.objects.prefetch_related('items__product')
  serializer_class = OrderSerializer


class UserOrderList(generics.ListAPIView):
  queryset = Order.objects.prefetch_related('items__product')
  serializer_class = OrderSerializer
  permission_classes = [permissions.IsAuthenticated]
  
  
  # can help with dynamic filtering
  def get_queryset(self):
    # user = self.request.user
    qs = super().get_queryset()
    return qs.filter(user=self.request.user)
  
# @api_view(['GET'])
# def product_info(request):
#   products = Product.objects.all()
#   serializer = ProductInfoSerializer({
#     'products':products,
#     'count':len(products),
#     'max_price': products.aggregate(max_price = Max('price'))['max_price']
#   })
  
#   return Response(serializer.data, status=200)  

class ProductInfo(APIView):
  def get(self, request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
      'products':products,
      'count':len(products),
      'max_price': products.aggregate(max_price = Max('price'))['max_price']
    })
    
    return Response(serializer.data)
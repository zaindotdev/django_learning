from rest_framework import serializers
from .models import Order, Product, OrderItem, User

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username')

class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ('id','name','price','stock')
    
    
    def validate_price(self, value):
      """
      Check that if the price is greater than 0.
      """
      
      if value<=0:
        raise serializers.ValidationError("Price must be greater than 0.")
      return value
      

class OrderItemSerializer(serializers.ModelSerializer):
  product_name = serializers.CharField(source="product.name")
  product_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.price')
  class Meta:
    model = OrderItem
    fields = ('product_name','product_price','quantity', 'item_subtotal')

class OrderSerializer(serializers.ModelSerializer):
  items = OrderItemSerializer(many=True, read_only=True)
  total_price = serializers.SerializerMethodField(method_name='total')
  user = UserSerializer(read_only=True)
  
  def total(self, obj):
    order_items = obj.items.all()
    
    return sum(order_item.item_subtotal for order_item in order_items)
  
  class Meta:
    model = Order
    fields = ('order_id', 'created_at', 'user', 'status', 'items', 'total_price')
    


class ProductInfoSerializer(serializers.Serializer):
  # get all the products, count of products, max price
  
  products = ProductSerializer(many=True)
  count = serializers.IntegerField()
  
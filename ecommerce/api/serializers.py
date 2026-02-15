from rest_framework import serializers
from .models import Order, Product, OrderItem, User
from django.db import transaction

class ProductSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ('id', 'name','description', 'price','stock')
    
    
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

class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product', 'quantity')
    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if orderitem_data is not None:
                # clear the existing items
                instance.items.all().delete()

                # Recreate items with the updated data
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)    
        return instance

    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            for item in orderitem_data:
                OrderItem.objects.create(order=order, **item)
        return order
    class Meta:
        model = Order
        fields = ("order_id", "user", "status", "items")
        extra_kwargs = {"user": {"read_only": True}}

class OrderSerializer(serializers.ModelSerializer):
  order_id  = serializers.UUIDField(read_only=True)
  items = OrderItemSerializer(many=True, read_only=True)
  total_price = serializers.SerializerMethodField(method_name='total')
  # user = UserSerializer(read_only=True)
  
  def total(self, obj):
    order_items = obj.items.all()
    
    return sum(order_item.item_subtotal for order_item in order_items)
  
  class Meta:
    model = Order
    fields = ('order_id', 'created_at', 'user', 'status', 'items', 'total_price')
  
  # def create(self, validated_data):
    # items_data = validated_data.pop('items')
    # pass


class ProductInfoSerializer(serializers.Serializer):
    # get all the products, count of products, max price

    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class UserSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "get_full_name", "orders")

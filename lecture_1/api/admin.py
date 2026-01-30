from django.contrib import admin
from api.models import Order, OrderItem

# Register your models here.
class OrderItemsInline(admin.TabularInline):
  model = OrderItem
class OrderAdmin(admin.ModelAdmin):
  inlines = [
    OrderItemsInline
  ]
  
admin.site.register(Order, OrderAdmin)
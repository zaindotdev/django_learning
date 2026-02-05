import django_filters
from api.models import Product
from rest_framework import filters

class ProductFilter(django_filters.FilterSet):
  class Meta:
    model = Product
    # fields = ('name', 'price') #filter by exact match
    
    fields = {
      'name':('icontains', 'iexact'),
      'price': ('gt', 'lt', 'range', 'exact')
    }
    

class InStockFilterBackend(filters.BaseFilterBackend):
  def filter_queryset(self, request, queryset, view):
    # return queryset.exclude(stock__gt=0)
    return queryset.filter(stock__gt=0)
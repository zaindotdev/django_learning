import django_filters
from api.models import Product

class ProductFilter(django_filters.FilterSet):
  class Meta:
    model = Product
    # fields = ('name', 'price') #filter by exact match
    
    fields = {
      'name':('icontains', 'iexact'),
      'price': ('gt', 'lt', 'range', 'exact')
    }
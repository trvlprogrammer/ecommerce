from django.contrib import admin

from .models import Order, OrderLines, Product

# Register your models here.

admin.site.register(Order)
admin.site.register(OrderLines)
admin.site.register(Product)

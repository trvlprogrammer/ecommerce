from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=300)
    price = models.FloatField()

    def __str__(self):
        return self.name


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class OrderLines(models.Model):
    item_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

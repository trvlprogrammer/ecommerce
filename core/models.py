from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse

CATEGORY_CHOICE = (("shirt", "SHIRT"), ("sport_wear", "SPORT WEAR"), ("outwear", "OUTWEAR"))
LABEL_CHOICE = (("P", "primary"), ("S", "secondary"), ("D", "danger"))


class Product(models.Model):
    name = models.CharField(max_length=300)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICE, max_length=20, default="shirt")
    label = models.CharField(choices=LABEL_CHOICE, max_length=20, default="P")
    slug = models.SlugField()
    description = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})


class OrderLines(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.product_id.name}"

    def get_total_item_price(self):
        return self.quantity * self.product_id.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product_id.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.product_id.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    order_lines = models.ManyToManyField(OrderLines)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user_id.username

    def get_total(self):
        total = 0
        for order_item in self.order_lines.all():
            total += order_item.get_final_price()
        # if self.coupon:
        #     total -= self.coupon.amount
        return total

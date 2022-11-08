from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Order, OrderLines, Product

# Create your views here.


def products(request):

    context = {"products": Product.objects.all()}

    return render(request, "product.html", context)


def checkout(request):

    context = {"products": Product.objects.all()}

    return render(request, "checkout.html", context)


class HomeView(ListView):
    model = Product
    template_name = "home.html"
    paginate_by = 10


class ProductDetailView(DetailView):
    model = Product
    template_name = "product.html"


def home(request):

    context = {"products": Product.objects.all()}

    return render(request, "home.html", context)


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_line, created = OrderLines.objects.get_or_create(product_id=product, user_id=request.user, ordered=False)
    order_qs = Order.objects.filter(user_id=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.order_lines.filter(product_id__slug=product.slug).exists():
            order_line.quantity += 1
            order_line.save()
            messages.info(request, "This product quantity was updated")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "This product was added to your cart")
            order.order_lines.add(order_line)
            order.save()
            return redirect("core:product", slug=slug)
    else:
        order = Order.objects.create(user_id=request.user, ordered_date=timezone.now)
        order.order_lines.add(order_line)
        messages.info(request, "This product was added to your cart")
        return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    order_qs = Order.objects.filter(user_id=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.order_lines.filter(product_id__slug=product.slug).exists():
            order_line = OrderLines.objects.filter(product_id=product, user_id=request.user, ordered=False)[0]
            order.order_lines.remove(order_line)
            messages.info(request, "This product was removed to your cart")
        else:
            messages.info(request, "This product was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

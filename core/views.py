from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

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


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user_id=self.request.user, ordered=False)
            context = {"object": order}
            return render(self.request, "order_summary.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


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
            order_line.delete()
            messages.info(request, "This product was removed to your cart")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This product was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user_id=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.order_lines.filter(product_id__slug=product.slug).exists():
            order_item = OrderLines.objects.filter(product_id=product, user_id=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.order_lines.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

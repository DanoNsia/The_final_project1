from django.shortcuts import get_object_or_404, render

from .models import Product


def product_list(request):

    products = Product.objects.all()

    context = {
        "products": products,
    }

    return render(
        request,
        "catalog/product_list.html",
        context,
    )


def product_detail(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    context = {
        "product": product,
    }

    return render(
        request,
        "catalog/product_detail.html",
        context,
    )

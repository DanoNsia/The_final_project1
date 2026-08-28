from django.contrib import admin

from .models import Order, OrderItem
from .telegram_utils import send_telegram_message

from django.contrib import admin

from .models import Order, OrderItem
from .telegram_utils import send_telegram_message


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    fields = (
        "product",
        "quantity",
        "get_total",
    )

    readonly_fields = (
        "product",
        "quantity",
        "get_total",
    )

    def get_total(self, obj):
        return f"{obj.total} ₽"

    get_total.short_description = "Сумма"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "created_at",
        "user",
        "phone",
        "address_short",
        "total_price_display",
        "status",
        "payment_status",
    )

    list_filter = (
        "status",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "id",
        "user__username",
        "user__email",
        "phone",
        "address",
        "comment",
    )

    list_editable = (
        "status",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        (
            "Информация о заказе",
            {
                "fields": (
                    "user",
                    "status",
                    "payment_status",
                    "created_at",
                )
            },
        ),
        (
            "Доставка",
            {
                "fields": (
                    "phone",
                    "address",
                    "comment",
                )
            },
        ),
        (
            "Стоимость",
            {
                "fields": (
                    "total_price_display",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "total_price_display",
    )

    inlines = [
        OrderItemInline,
    ]

    def address_short(self, obj):

        if len(obj.address) > 35:
            return obj.address[:35] + "..."

        return obj.address

    address_short.short_description = "Адрес"

    def total_price_display(self, obj):
        return f"{obj.total_price} ₽"

    total_price_display.short_description = "Итого"
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'updated_at')  # отображаемые поля
    list_filter = ('created_at', 'updated_at')  # фильтры
    search_fields = ('name', 'description')  # поиск по названию и описанию
    readonly_fields = ('created_at', 'updated_at')  # только для чтения

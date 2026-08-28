from django.db import models


class Product(models.Model):
    name = models.CharField(
        "Название",
        max_length=255
    )

    description = models.TextField(
        "Описание"
    )

    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        "Изображение",
        upload_to="products/",
        blank=True,
        null=True
    )

    image_url = models.URLField(
        "Ссылка на изображение",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        "Создан",
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        "Изменён",
        auto_now=True
    )

    class Meta:
        verbose_name = "Букет"
        verbose_name_plural = "Букеты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

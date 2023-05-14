from django.db import models
from django.utils import timezone


class Address(models.Model):
    address = models.CharField(
        'адрес места',
        max_length=150,
        unique=True
    )
    longitude = models.DecimalField(
        'долгота',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    latitude = models.DecimalField(
        'широта',
        max_digits=9,
        decimal_places=6
    )
    created_at = models.DateTimeField(
        'время создания',
        default=timezone.now,
        db_index=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return self.address

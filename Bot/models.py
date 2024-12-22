from django.db import models

# Create your models here.
from django.db import models

class TelegramUser(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
    ]

    user_id = models.BigIntegerField(unique=True, verbose_name="Telegram User ID")
    first_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="First Name")
    last_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="Last Name")
    username = models.CharField(max_length=256, blank=True, null=True, verbose_name="Username")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    last_active = models.DateTimeField(auto_now=True, verbose_name="Last Active")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="User Status"
    )
    is_admin = models.BooleanField(default=False, verbose_name="Is Admin")  # Admin belgilovchi ustun
    extra_info = models.JSONField(blank=True, null=True, verbose_name="Extra Information")  # Qo'shimcha ma'lumotlar

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
        ordering = ['-last_active']

    def __str__(self):
        return f"{self.first_name} {self.last_name} (@{self.username})" if self.username else f"{self.user_id}"

    @classmethod
    def get_admin_ids(cls):
        """
        Admin bo'lgan userlarning IDlarini qaytaradi.
        """
        return list(cls.objects.filter(is_admin=True).values_list('user_id', flat=True))

    @classmethod
    def get_active_user_ids(cls):
        """
        Statusi "active" bo'lgan userlarning IDlarini qaytaradi.
        """
        return list(cls.objects.filter(status='active').values_list('user_id', flat=True))

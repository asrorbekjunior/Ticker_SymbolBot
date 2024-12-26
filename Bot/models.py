from django.db import models, transaction
from django.db.models import Count
from django.utils.timezone import now
from time import sleep
from telegram import Bot
from telegram.error import TelegramError


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
    is_admin = models.BooleanField(default=False, verbose_name="Is Admin")

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

    @classmethod
    def get_today_new_users(cls):
        """
        Bugungi yangi foydalanuvchilarni qaytaradi.
        """
        today = now().date()
        return cls.objects.filter(date_joined__date=today)

    @classmethod
    def get_daily_new_users(cls):
        """
        Har bir kun uchun yangi foydalanuvchilar sonini qaytaradi.
        """
        return cls.objects.values('date_joined__date').annotate(count=Count('id')).order_by('-date_joined__date')

    @classmethod
    def get_total_users(cls):
        """
        Umumiy foydalanuvchilar sonini qaytaradi.
        """
        return cls.objects.count()

    @classmethod
    def count_active_users(cls):
        """
        Statusi 'active' bo'lgan foydalanuvchilar sonini qaytaradi.
        """
        return cls.objects.filter(status='active').count()

    @classmethod
    def count_admin_users(cls):
        """
        Admin bo'lgan foydalanuvchilar sonini qaytaradi.
        """
        return cls.objects.filter(is_admin=True).count()

    @classmethod
    @transaction.atomic
    def find_and_block_inactive_users(cls, bot_token):
        """
        Nofaol foydalanuvchilarni aniqlab, ularning statusini 'blocked' ga o'zgartiradi.
        :param bot_token: Telegram bot tokeni
        :return: Bloklangan foydalanuvchilar soni
        """
        bot = Bot(token=bot_token)
        blocked_users_count = 0

        for user in cls.objects.all():
            try:
                # Foydalanuvchiga chat action yuborish
                bot.send_chat_action(chat_id=user.user_id, action="typing")
                sleep(0.1)  # Telegram API cheklovlarini e'tiborga olish
            except TelegramError as e:
                # Faqat botni bloklaganlar uchun statusni yangilash
                if "bot was blocked by the user" in str(e) or "user is deactivated" in str(e):
                    user.status = 'blocked'
                    user.save(update_fields=['status'])
                    blocked_users_count += 1
                else:
                    # Boshqa xatoliklar uchun log yaratish
                    print(f"Error for user {user.user_id}: {e}")

        return blocked_users_count
    @classmethod
    @transaction.atomic
    def make_admin(cls, user_id):
        """
        Userni admin qiladi.
        :param user_id: Admin qilinadigan foydalanuvchining Telegram user_id-si
        :return: Yangilangan user obyekti yoki None (user topilmasa)
        """
        try:
            user = cls.objects.get(user_id=user_id)
            user.is_admin = True
            user.save(update_fields=['is_admin'])
            return user
        except cls.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")
            return None

    @classmethod
    @transaction.atomic
    def remove_admin(cls, user_id):
        """
        Userni adminlikdan chiqaradi.
        :param user_id: Adminlikdan chiqariladigan foydalanuvchining Telegram user_id-si
        :return: Yangilangan user obyekti yoki None (user topilmasa)
        """
        try:
            user = cls.objects.get(user_id=user_id)
            user.is_admin = False
            user.save(update_fields=['is_admin'])
            return user
        except cls.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")
            return None


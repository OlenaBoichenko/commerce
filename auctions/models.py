from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        'Listing', related_name="watched_by", blank=True)  # Поле Watchlist


class Listing(models.Model):
    title = models.CharField(max_length=255)  # Заголовок объявления
    description = models.TextField()  # Описание объявления
    starting_bid = models.DecimalField(
        max_digits=10, decimal_places=2)  # Начальная ставка
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    # URL изображения (опционально)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100)  # Категория объявления
    created_at = models.DateTimeField(
        auto_now_add=True)  # Дата создания объявления
    is_active = models.BooleanField(default=True)  # Активность объявления
    owner = models.ForeignKey(
        'User', on_delete=models.CASCADE)  # Владелец объявления

    def __str__(self):
        return self.title  # Для отображения заголовка в админке


class Bid(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")  # Связь с объявлением
    bid_amount = models.DecimalField(
        max_digits=10, decimal_places=2)  # Сумма ставки
    # Пользователь, сделавший ставку
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_time = models.DateTimeField(auto_now_add=True)  # Время ставки

    def __str__(self):
        return f"Bid of ${self.bid_amount} by {self.bidder.username} on {self.listing.title}"


class Comment(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE)  # Связь с объявлением
    # Пользователь, оставивший комментарий
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField()  # Текст комментария
    created_at = models.DateTimeField(
        auto_now_add=True)  # Дата добавления комментария

    def __str__(self):
        return f"Comment by {self.user.username} on {self.listing.title}"

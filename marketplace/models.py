from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Item(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.original_price is None:
            self.original_price = self.price
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        SearchHistory.objects.filter(query=self.title).delete()
        super().delete(*args, **kwargs)

    @property
    def average_rating(self):
        avg = self.ratings.aggregate(Avg('stars'))['stars__avg']
        return avg if avg is not None else 0.0
    @property
    def is_deal(self):
        """Check if the item is a deal (price lower than original price)."""
        return self.price < self.original_price

    @property
    def discount_percentage(self):
        """Calculate the discount percentage."""
        if self.original_price > self.price:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return round(discount, 2)
        return 0.0

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=200)
    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Search by {self.user.username}: {self.query}'


class UserRating(models.Model):
    item = models.ForeignKey(Item, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Rating by {self.user.username} for {self.item.title}'

from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=150)
    cover = models.CharField(max_length=150, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return (
            f"Title: {self.title}; "
            f"Author: {self.author}; "
            f"Inventory: {self.inventory}; "
            f"Daily Fee: {self.daily_fee}"
            )

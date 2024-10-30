from django.db import models
from books.models import Book
from django.conf import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(null=False, blank=False)
    expected_return_date = models.DateField(null=False, blank=False)
    actual_return_date = models.DateField(null=False, blank=False)
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing",
        db_column="book_id"
    )
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowing",
        db_column="user_id"
    )

    def __str__(self):
        return f"User {self.user_id}, book {self.book_id}"

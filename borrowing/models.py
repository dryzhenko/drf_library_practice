from django.db import models


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book_id = models.IntegerField()
    user_id = models.IntegerField()

    def __str__(self):
        return f"User {self.user_id}, book {self.book_id}"

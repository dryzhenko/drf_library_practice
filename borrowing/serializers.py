from rest_framework import serializers

from borrowing.models import Borrowing

from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book_id", "user_id")


class BorrowingListSerializer(BorrowingSerializer):
    book_id = BookSerializer()

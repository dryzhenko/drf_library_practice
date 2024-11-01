from django.utils import timezone
from rest_framework import serializers

from borrowing.models import Borrowing

from books.serializers import BookSerializer
from telegram_bot import notify_borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book_id", "user_id")


class BorrowingListSerializer(BorrowingSerializer):
    book_id = BookSerializer()


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book_id", "user_id")
        read_only_fields = ("user_id",)

    def create(self, validated_data):
        book = validated_data.get("book_id")

        book.inventory -= 1
        book.save()

        user = self.context["request"].user
        validated_data["user_id"] = user

        borrowing = Borrowing.objects.create(**validated_data)

        notify_borrowing(book, user)

        return borrowing

    def validate(self, attrs):
        book = attrs.get("book_id")

        if book.inventory == 0:
            raise serializers.ValidationError({"book_id": "This book is out of stock"})

        return attrs


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError("This book has already been returned")

        return attrs

    def update(self, instance, validated_data):
        book = instance.book_id
        book.inventory += 1
        book.save()

        instance.actual_return_date = timezone.now().date()
        instance.save()

        return instance

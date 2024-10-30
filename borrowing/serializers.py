from rest_framework import serializers

from borrowing.models import Borrowing

from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book_id", "user_id")


class BorrowingListSerializer(BorrowingSerializer):
    book_id = BookSerializer()


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("borrow_date", "expected_return_date", "book_id", "user_id")

    def create(self, validated_data):
        book = validated_data.get("book_id")

        book.inventory -= 1
        book.save()

        return Borrowing.objects.create(**validated_data)

    def validate(self, attrs):
        book = attrs.get("book_id")

        if book.inventory == 0:
            raise serializers.ValidationError({"book_id": "This book is out of stock"})

        return attrs

from django.test import TestCase
from books.models import Book
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from books.serializers import BookSerializer
from rest_framework.test import APIRequestFactory
from books.permissions import IsAdminOrReadOnly


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=5.00
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.cover, "HARD")
        self.assertEqual(self.book.inventory, 10)
        self.assertEqual(self.book.daily_fee, 5.00)

    def test_book_str(self):
        self.assertEqual(
            str(self.book),
            "Title: Test Book; Author: Test Author; Inventory: 10; Daily Fee: 5.0"
        )


class BookSerializerTest(APITestCase):
    def setUp(self):
        self.book_data = {
            "title": "Serialized Book",
            "author": "Serialized Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 4.50
        }
        self.book = Book.objects.create(**self.book_data)

    def test_serializer_contains_correct_fields(self):
        serializer = BookSerializer(instance=self.book)
        data = serializer.data
        self.assertEqual(set(data.keys()), {"title", "author", "cover", "inventory", "daily_fee"})

    def test_serializer_data(self):
        serializer = BookSerializer(instance=self.book)
        self.assertEqual(serializer.data["title"], "Serialized Book")
        self.assertEqual(serializer.data["author"], "Serialized Author")
        self.assertEqual(serializer.data["cover"], "SOFT")
        self.assertEqual(serializer.data["inventory"], 5)
        self.assertEqual(float(serializer.data["daily_fee"]), 4.50)


class IsAdminOrReadOnlyTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(email="testuser@example.com", password="password")
        self.admin_user = get_user_model().objects.create_superuser(email="adminuser@example.com", password="password")
        self.permission = IsAdminOrReadOnly()

    def test_permission_for_safe_method(self):
        request = self.factory.get("/books/")
        request.user = self.user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_permission_for_non_admin_user(self):
        request = self.factory.post("/books/")
        request.user = self.user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_permission_for_admin_user(self):
        request = self.factory.post("/books/")
        request.user = self.admin_user
        self.assertTrue(self.permission.has_permission(request, None))


class BookViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(email="adminuser@example.com", password="password")
        self.book = Book.objects.create(
            title="API Book",
            author="API Author",
            cover="HARD",
            inventory=3,
            daily_fee=3.50
        )
        self.book_url = reverse('books:books-list')

    def test_list_books(self):
        response = self.client.get(self.book_url)
        self.assertEqual(response.status_code, 200)

    def test_create_book_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "title": "New API Book",
            "author": "New API Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 4.00
        }
        response = self.client.post(self.book_url, data)
        self.assertEqual(response.status_code, 201)

    def test_create_book_as_non_admin(self):
        user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.client.force_authenticate(user=user)
        data = {
            "title": "New API Book",
            "author": "New API Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 4.00
        }
        response = self.client.post(self.book_url, data)
        self.assertEqual(response.status_code, 403)


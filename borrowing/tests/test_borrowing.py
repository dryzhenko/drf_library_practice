from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from books.models import Book
from borrowing.models import Borrowing
from django.contrib.auth import get_user_model
from django.utils import timezone


class BorrowingCreateTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.book = Book.objects.create(title="Test Book", author="Author", cover="HARD", inventory=1, daily_fee=5.00)
        self.borrowing_url = reverse("borrowing:borrowing-list")
        self.client.force_authenticate(user=self.user)

    def test_create_borrowing_decreases_inventory(self):
        data = {
            "borrow_date": timezone.now().date(),
            "expected_return_date": (timezone.now() + timezone.timedelta(days=7)).date(),
            "book_id": self.book.id,
        }
        response = self.client.post(self.borrowing_url, data)
        self.assertEqual(response.status_code, 201)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 0)

    def test_cannot_borrow_out_of_stock_book(self):
        self.book.inventory = 0
        self.book.save()
        data = {
            "borrow_date": timezone.now().date(),
            "expected_return_date": (timezone.now() + timezone.timedelta(days=7)).date(),
            "book_id": self.book.id,
        }
        response = self.client.post(self.borrowing_url, data)
        self.assertEqual(response.status_code, 400)


class BorrowingReturnTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.book = Book.objects.create(title="Test Book", author="Author", cover="HARD", inventory=0, daily_fee=5.00)
        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=(timezone.now() + timezone.timedelta(days=7)).date(),
            book_id=self.book,
            user_id=self.user
        )
        self.return_url = reverse("borrowing:borrowing-return-borrowing", args=[self.borrowing.id])
        self.client.force_authenticate(user=self.user)

    def test_return_borrowing_increases_inventory(self):
        data = {"actual_return_date": timezone.now().date()}
        response = self.client.get(self.return_url, data)
        self.assertEqual(response.status_code, 201)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

    def test_cannot_return_already_returned_book(self):
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()
        data = {"actual_return_date": timezone.now().date()}
        response = self.client.get(self.return_url, data)
        self.assertEqual(response.status_code, 400)


class BorrowingFilterTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email="user@example.com", password="password")
        self.book = Book.objects.create(title="Test Book", author="Author", cover="HARD", inventory=1, daily_fee=5.00)
        self.borrowing_active = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=(timezone.now() + timezone.timedelta(days=7)).date(),
            book_id=self.book,
            user_id=self.user
        )
        self.borrowing_inactive = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=(timezone.now() + timezone.timedelta(days=7)).date(),
            actual_return_date=timezone.now().date(),
            book_id=self.book,
            user_id=self.user
        )
        self.borrowing_url = reverse("borrowing:borrowing-list")
        self.client.force_authenticate(user=self.user)

    def test_filter_active_borrowings(self):
        response = self.client.get(self.borrowing_url, {"is_active": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing_active.id)

    def test_filter_inactive_borrowings(self):
        response = self.client.get(self.borrowing_url, {"is_active": "false"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing_inactive.id)

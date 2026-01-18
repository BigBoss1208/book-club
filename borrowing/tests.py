from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from library.models import Category, Book
from .models import BorrowRequest, BorrowTransaction


class BorrowingWorkflowTests(TestCase):
    """Smoke tests for borrow request workflow and permissions."""

    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.user = User.objects.create_user(username='user', password='user123')

        cat = Category.objects.create(name='Test', description='')
        self.book = Book.objects.create(
            title='Test Book',
            author='Author',
            publisher='Pub',
            publish_year=2022,
            category=cat,
            total_copies=1,
            available_copies=1,
            is_active=True,
        )

    def test_user_creates_borrow_request(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse('borrowing:create_request', args=[self.book.pk]), {
            'expected_return_date': timezone.now().date(),
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(BorrowRequest.objects.filter(user=self.user, book=self.book).exists())

    def test_admin_approves_request_creates_transaction_and_decreases_stock(self):
        # user create
        self.client.force_login(self.user)
        self.client.post(reverse('borrowing:create_request', args=[self.book.pk]), {
            'expected_return_date': timezone.now().date(),
        })
        br = BorrowRequest.objects.get(user=self.user, book=self.book)

        # admin approves
        self.client.force_login(self.admin)
        resp = self.client.post(reverse('borrowing:approve_request', args=[br.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)

        br.refresh_from_db()
        self.book.refresh_from_db()

        self.assertEqual(br.status, 'APPROVED')
        self.assertEqual(self.book.available_copies, 0)
        self.assertTrue(BorrowTransaction.objects.filter(borrow_request=br).exists())

    def test_admin_returns_book_increases_stock(self):
        # create + approve
        self.client.force_login(self.user)
        self.client.post(reverse('borrowing:create_request', args=[self.book.pk]), {
            'expected_return_date': timezone.now().date(),
        })
        br = BorrowRequest.objects.get(user=self.user, book=self.book)

        self.client.force_login(self.admin)
        self.client.post(reverse('borrowing:approve_request', args=[br.pk]))
        tx = BorrowTransaction.objects.get(borrow_request=br)

        # return
        resp = self.client.post(reverse('borrowing:return_book', args=[tx.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)

        tx.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(tx.status, 'RETURNED')
        self.assertEqual(self.book.available_copies, 1)

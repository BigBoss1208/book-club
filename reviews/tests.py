from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from library.models import Category, Book
from borrowing.models import BorrowRequest, BorrowTransaction
from .models import Review


class ReviewWorkflowTests(TestCase):
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

    def _create_returned_transaction(self):
        br = BorrowRequest.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date(),
            status='APPROVED',
            handled_by=self.admin,
            handled_at=timezone.now(),
        )
        tx = BorrowTransaction.objects.create(
            borrow_request=br,
            due_at=timezone.now(),
            status='RETURNED',
            returned_at=timezone.now(),
        )
        return tx

    def test_user_cannot_review_if_not_returned(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('reviews:create_review', args=[self.book.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Review.objects.filter(user=self.user, book=self.book).exists())

    def test_user_creates_review_then_admin_approves(self):
        self._create_returned_transaction()

        self.client.force_login(self.user)
        resp = self.client.post(reverse('reviews:create_review', args=[self.book.pk]), {
            'rating': 5,
            'content': 'Sách rất hay!'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        review = Review.objects.get(user=self.user, book=self.book)
        self.assertEqual(review.status, 'PENDING')

        self.client.force_login(self.admin)
        resp = self.client.post(reverse('reviews:approve_review', args=[review.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)

        review.refresh_from_db()
        self.assertEqual(review.status, 'APPROVED')

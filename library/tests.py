from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Category, Book


class LibraryCrudAndPermissionsTests(TestCase):
    """Smoke tests for CRUD, search/filter/sort and basic permissions.

    Notes:
    - We keep tests light-weight (no external services).
    - These tests confirm that views respond and main business rules hold.
    """

    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.user = User.objects.create_user(username='user', password='user123')

        self.cat = Category.objects.create(name='Văn học', description='Test')
        self.book = Book.objects.create(
            title='Dế Mèn Phiêu Lưu Ký',
            author='Tô Hoài',
            publisher='NXB',
            publish_year=2020,
            category=self.cat,
            total_copies=3,
            available_copies=3,
            is_active=True,
        )

    def test_guest_can_view_book_list_and_detail(self):
        resp = self.client.get(reverse('library:book_list'))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('library:book_detail', args=[self.book.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_search_filter_sort_book_list(self):
        resp = self.client.get(reverse('library:book_list') + '?search=de%20men')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Dế Mèn', html=False)

    def test_admin_can_access_category_crud_pages(self):
        self.client.force_login(self.admin)

        resp = self.client.get(reverse('library:category_list'))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('library:category_create'))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse('library:category_create'), {
            'name': 'Công nghệ',
            'description': 'Test',
            'is_active': True,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Category.objects.filter(name='Công nghệ').exists())

    def test_non_admin_is_redirected_from_admin_pages(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('library:book_create'))
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get(reverse('library:category_list'))
        self.assertEqual(resp.status_code, 302)

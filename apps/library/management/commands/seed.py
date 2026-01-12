from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

from apps.accounts.models import StudentProfile
from apps.library.models import Category, Book
from apps.borrowing.models import BorrowRequest, BorrowRequestStatus, BorrowTransaction, BorrowTransactionStatus
from apps.reviews.models import Review, ReviewStatus

class Command(BaseCommand):
    help = "Seed sample data for BookClub (full 7 entities)"

    def handle(self, *args, **options):
        # Admin
        admin, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})
        if created:
            admin.set_password("Admin@123")
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
        else:
            if not admin.is_staff:
                admin.is_staff = True
                admin.is_superuser = True
                admin.save()

        # Students
        sv001, created = User.objects.get_or_create(username="sv001", defaults={"email": "sv001@example.com"})
        if created:
            sv001.set_password("Student@123")
            sv001.save()

        sv002, created = User.objects.get_or_create(username="sv002", defaults={"email": "sv002@example.com"})
        if created:
            sv002.set_password("Student@123")
            sv002.save()

        # StudentProfile 1-1
        StudentProfile.objects.get_or_create(
            user=sv001,
            defaults={
                "student_code": "SV001",
                "full_name": "Nguyễn Văn A",
                "phone": "0900000001",
                "faculty": "CNTT",
                "class_name": "KTPM01",
            }
        )
        StudentProfile.objects.get_or_create(
            user=sv002,
            defaults={
                "student_code": "SV002",
                "full_name": "Trần Thị B",
                "phone": "0900000002",
                "faculty": "Kinh tế",
                "class_name": "QTKD02",
            }
        )

        # Categories
        cat1, _ = Category.objects.get_or_create(name="Văn học", defaults={"description": "Sách văn học"})
        cat2, _ = Category.objects.get_or_create(name="Kỹ năng", defaults={"description": "Sách kỹ năng"})
        cat3, _ = Category.objects.get_or_create(name="CNTT", defaults={"description": "Sách công nghệ"})

        # Books
        b1, _ = Book.objects.get_or_create(
            title="Nhà giả kim",
            defaults={"author": "Paulo Coelho", "category": cat1, "total_copies": 5, "available_copies": 5, "created_by": admin}
        )
        b2, _ = Book.objects.get_or_create(
            title="Đắc nhân tâm",
            defaults={"author": "Dale Carnegie", "category": cat2, "total_copies": 5, "available_copies": 4, "created_by": admin}
        )
        b3, _ = Book.objects.get_or_create(
            title="Clean Code",
            defaults={"author": "Robert C. Martin", "category": cat3, "total_copies": 3, "available_copies": 2, "created_by": admin}
        )

        # BorrowRequests (Approved / Pending / Rejected)
        r1, _ = BorrowRequest.objects.get_or_create(
            user=sv001, book=b3,
            defaults={
                "expected_return_date": date.today() + timedelta(days=7),
                "status": BorrowRequestStatus.APPROVED,
                "handled_by": admin,
                "handled_at": timezone.now(),
                "note": "Approved sample"
            }
        )

        BorrowRequest.objects.get_or_create(
            user=sv001, book=b2,
            defaults={
                "expected_return_date": date.today() + timedelta(days=10),
                "status": BorrowRequestStatus.PENDING,
                "note": "Pending sample"
            }
        )

        BorrowRequest.objects.get_or_create(
            user=sv002, book=b1,
            defaults={
                "expected_return_date": date.today() + timedelta(days=5),
                "status": BorrowRequestStatus.REJECTED,
                "handled_by": admin,
                "handled_at": timezone.now(),
                "note": "Rejected sample"
            }
        )

        # BorrowTransaction 1-1 for approved request
        BorrowTransaction.objects.get_or_create(
            borrow_request=r1,
            defaults={
                "borrowed_at": timezone.now(),
                "due_at": timezone.now() + timedelta(days=7),
                "status": BorrowTransactionStatus.BORROWING
            }
        )

        # Reviews (Approved + Pending)
        Review.objects.get_or_create(
            user=sv002,
            book=b1,
            defaults={
                "rating": 5,
                "content": "Sách hay, truyền cảm hứng.",
                "status": ReviewStatus.APPROVED,
                "moderated_by": admin,
                "moderated_at": timezone.now(),
            }
        )

        tx = r1.transaction
        Review.objects.get_or_create(
            user=sv001,
            book=b3,
            borrow_transaction=tx,
            defaults={
                "rating": 4,
                "content": "Nội dung thực tế, phù hợp luyện coding.",
                "status": ReviewStatus.PENDING
            }
        )

        self.stdout.write(self.style.SUCCESS("Seed OK: Users + Profiles + Categories + Books + Borrow + Transaction + Reviews"))

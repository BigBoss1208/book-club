import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from library.models import Category, Book
from accounts.models import StudentProfile
from borrowing.models import BorrowRequest, BorrowTransaction

# ============================================================
# Tạo tài khoản admin
# ============================================================
admin_user, admin_created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'first_name': 'System',
        'last_name': 'Admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if admin_created:
    admin_user.set_password('admin@123')
    admin_user.save()
    print("✅ Created admin user: admin/admin@123")
else:
    updated = False
    if not admin_user.is_staff:
        admin_user.is_staff = True
        updated = True
    if not admin_user.is_superuser:
        admin_user.is_superuser = True
        updated = True
    if updated:
        admin_user.save()
        print("✅ Updated admin user permissions")

# ============================================================
# Tạo categories
# ============================================================
categories_data = [
    {'name': 'Văn học', 'description': 'Sách văn học trong và ngoài nước'},
    {'name': 'Kỹ năng sống', 'description': 'Phát triển bản thân và kỹ năng mềm'},
    {'name': 'Công nghệ', 'description': 'Sách về lập trình và công nghệ'},
    {'name': 'Kinh tế', 'description': 'Kinh doanh và quản trị'},
]

for cat_data in categories_data:
    Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    print(f"✅ Created category: {cat_data['name']}")

# ============================================================
# Tạo users mẫu
# ============================================================
sample_users_data = [
    {'username': 'student01', 'first_name': 'Nguyen', 'last_name': 'Van A', 'email': 'student01@example.com', 'student_code': 'SV001', 'phone': '0123456789'},
    {'username': 'student02', 'first_name': 'Tran',   'last_name': 'Thi B', 'email': 'student02@example.com', 'student_code': 'SV002', 'phone': '0987654321'},
    {'username': 'student03', 'first_name': 'Le',     'last_name': 'Van C',  'email': 'student03@example.com', 'student_code': 'SV003', 'phone': '0912345678'},
    {'username': 'student04', 'first_name': 'Pham',   'last_name': 'Thi D', 'email': 'student04@example.com', 'student_code': 'SV004', 'phone': '0911222333'},
    {'username': 'student05', 'first_name': 'Hoang',  'last_name': 'Van E',  'email': 'student05@example.com', 'student_code': 'SV005', 'phone': '0922333444'},
]

created_users = []
for u in sample_users_data:
    user, created = User.objects.get_or_create(
        username=u['username'],
        defaults={
            'email': u['email'],
            'first_name': u['first_name'],
            'last_name': u['last_name'],
        }
    )
    if created:
        user.set_password('student123')
        user.save()
        print(f"✅ Created user: {u['username']}/student123")

    StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            'student_code': u['student_code'],
            'full_name': f"{u['first_name']} {u['last_name']}",
            'phone': u['phone'],
            'faculty': 'Công nghệ thông tin',
            'class_name': 'CNTT01',
        }
    )
    created_users.append(user)

# ============================================================
# Tạo sách mẫu
# ============================================================
categories_obj = {cat.name: cat for cat in Category.objects.all()}

books_data = [
    {'title': 'Clean Code',                 'author': 'Robert C. Martin',  'publisher': 'Prentice Hall',        'publish_year': 2008, 'description': 'A Handbook of Agile Software Craftsmanship',               'total_copies': 5,  'available_copies': 5,  'category': categories_obj.get('Công nghệ')},
    {'title': 'Sapiens: Lược sử loài người','author': 'Yuval Noah Harari', 'publisher': 'NXB Trẻ',              'publish_year': 2018, 'description': 'Từ khi xuất hiện đến nay, loài người đã trải qua những gì?','total_copies': 10, 'available_copies': 10, 'category': categories_obj.get('Văn học')},
    {'title': 'Đắc nhân tâm',               'author': 'Dale Carnegie',     'publisher': 'NXB Tổng hợp TP.HCM', 'publish_year': 2015, 'description': 'Nghệ thuật thu phục lòng người',                          'total_copies': 8,  'available_copies': 8,  'category': categories_obj.get('Kỹ năng sống')},
    {'title': 'Rich Dad Poor Dad',          'author': 'Robert Kiyosaki',   'publisher': 'NXB Trẻ',              'publish_year': 2016, 'description': 'Cha giàu cha nghèo',                                      'total_copies': 6,  'available_copies': 6,  'category': categories_obj.get('Kinh tế')},
    {'title': 'Lập Trình Python Cơ Bản',    'author': 'Nguyen Van X',      'publisher': 'NXB KHKT',             'publish_year': 2020, 'description': 'Học Python từ cơ bản đến nâng cao',                       'total_copies': 7,  'available_copies': 7,  'category': categories_obj.get('Công nghệ')},
    {'title': 'Truyện Kiều',                'author': 'Nguyễn Du',         'publisher': 'NXB Văn học',          'publish_year': 2010, 'description': 'Kiệt tác văn học Việt Nam',                               'total_copies': 4,  'available_copies': 4,  'category': categories_obj.get('Văn học')},
    {'title': 'Pride and Prejudice',        'author': 'Jane Austen',       'publisher': 'Penguin',              'publish_year': 1813, 'description': 'Classic English novel',                                   'total_copies': 3,  'available_copies': 3,  'category': categories_obj.get('Văn học')},
]

for book_data in books_data:
    book_data['created_by'] = admin_user
    book, created = Book.objects.get_or_create(
        title=book_data['title'],
        defaults=book_data
    )
    if created:
        print(f"✅ Created book: {book.title}")

# ============================================================
# Tạo dữ liệu mượn sách 30 ngày qua
# ============================================================
print("\n📚 Đang tạo dữ liệu mượn sách...")

# Xóa dữ liệu mượn cũ để tránh trùng
BorrowTransaction.objects.all().delete()
BorrowRequest.objects.all().delete()
print("🗑️  Đã xóa dữ liệu mượn cũ")

books = list(Book.objects.filter(is_active=True))
users = list(User.objects.filter(is_staff=False, is_active=True))
today = timezone.now()

for i in range(30):
    request_date = today - timedelta(days=29 - i)
    num_borrows = random.randint(1, 4)  # Mỗi ngày 1-4 lượt mượn

    for _ in range(num_borrows):
        book = random.choice(books)
        user = random.choice(users)

        expected_return = request_date + timedelta(days=14)

        # Tạo BorrowRequest
        borrow_request = BorrowRequest(
            user=user,
            book=book,
            status='APPROVED',
            expected_return_date=expected_return.date(),
            handled_by=admin_user,
            handled_at=request_date + timedelta(hours=1),
        )
        borrow_request.save()

        # Ép request_date về quá khứ (vì field là auto_now_add)
        BorrowRequest.objects.filter(pk=borrow_request.pk).update(
            request_date=request_date
        )

        # Tạo BorrowTransaction
        due_at = request_date + timedelta(days=14)
        returned_at = request_date + timedelta(days=random.randint(3, 13))

        transaction = BorrowTransaction(
            borrow_request=borrow_request,
            due_at=due_at,
            returned_at=returned_at,
            status='RETURNED',
            fine_amount=0,
        )
        transaction.save()

        # Ép borrowed_at về quá khứ (vì field là auto_now_add)
        BorrowTransaction.objects.filter(pk=transaction.pk).update(
            borrowed_at=request_date
        )

print("✅ Đã tạo dữ liệu mượn sách cho 30 ngày qua!")
print("\n🎉 Hoàn thành! Dữ liệu mẫu đã được tạo thành công!")
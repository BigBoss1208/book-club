import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from django.contrib.auth.models import User
from library.models import Category, Book
from accounts.models import StudentProfile

# Tạo tài khoản admin trước
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
        print("✅ Updated admin user permissions: admin")

# Tạo categories
categories = [
    {'name': 'Văn học', 'description': 'Sách văn học trong và ngoài nước'},
    {'name': 'Kỹ năng sống', 'description': 'Phát triển bản thân và kỹ năng mềm'},
    {'name': 'Công nghệ', 'description': 'Sách về lập trình và công nghệ'},
    {'name': 'Kinh tế', 'description': 'Kinh doanh và quản trị'},
]

for cat_data in categories:
    Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    print(f"✅ Created category: {cat_data['name']}")

# Tạo user mẫu
user, created = User.objects.get_or_create(
    username='student01',
    defaults={
        'email': 'student01@example.com',
        'first_name': 'Nguyen',
        'last_name': 'Van A'
    }
)
if created:
    user.set_password('student123')
    user.save()
    print("✅ Created sample user: student01/student123")

StudentProfile.objects.get_or_create(
    user=user,
    defaults={
        'student_code': 'SV001',
        'full_name': 'Nguyen Van A',
        'phone': '0123456789',
        'faculty': 'Công nghệ thông tin',
        'class_name': 'CNTT01'
    }
)

# Tạo sách mẫu
category = Category.objects.first()

books_data = [
    {
        'title': 'Clean Code',
        'author': 'Robert C. Martin',
        'publisher': 'Prentice Hall',
        'publish_year': 2008,
        'description': 'A Handbook of Agile Software Craftsmanship',
        'total_copies': 5,
        'available_copies': 5,
    },
    {
        'title': 'Sapiens: Lược sử loài người',
        'author': 'Yuval Noah Harari',
        'publisher': 'NXB Trẻ',
        'publish_year': 2018,
        'description': 'Từ khi xuất hiện đến nay, loài người đã trải qua những gì?',
        'total_copies': 10,
        'available_copies': 10,
    },
    {
        'title': 'Đắc nhân tâm',
        'author': 'Dale Carnegie',
        'publisher': 'NXB Tổng hợp TP.HCM',
        'publish_year': 2015,
        'description': 'Nghệ thuật thu phục lòng người',
        'total_copies': 8,
        'available_copies': 8,
    },
]

for book_data in books_data:
    book_data['category'] = category
    book_data['created_by'] = admin_user
    book, created = Book.objects.get_or_create(
        title=book_data['title'],
        defaults=book_data
    )
    if created:
        print(f"✅ Created book: {book.title}")

print("\n🎉 Dữ liệu mẫu đã được tạo thành công!")

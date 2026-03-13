# BookClub Library Management System

**Mục tiêu**

* Quản lý thư viện sách: danh mục, sách, mượn/trả và đánh giá.
* Cung cấp giao diện cho người dùng và trang quản trị cho nhân viên.
* Có dữ liệu mẫu để test nhanh các chức năng chính.
## Cài Đặt

### 1) Tạo và kích hoạt virtual environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 2) Cài Đặt dependencies
```powershell
pip install -r requirements.txt
```

### 3) Thiết lập database
- Chạy file `schema` để tạo   database va bảng.
- Cập nhập thông tin kết nối `.env`.

### 4) Migrate va tạo dữ liệu mẫu
```powershell
python manage.py makemigrations
python manage.py migrate
python create_sample_data.py
```

### 5) Chạy server
```powershell
python manage.py runserver
```

## Tài Khoản Mẫu
- Admin: `admin` / `admin@123`
- User mau: `student01` / `student123`

## URL tham khao
- Trang chu: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Danh sach sach: http://127.0.0.1:8000/library/books/

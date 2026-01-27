# BookClub Library System

## Muc tieu
- Quan ly thu vien sach: danh muc, sach, muon/tra, va danh gia.
- Cung cap giao dien cho nguoi dung va trang quan tri cho nhan vien.
- Co du lieu mau de test nhanh cac chuc nang chinh.

## Cai dat

### 1) Tao va kich hoat virtual environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 2) Cai dat dependencies
```powershell
pip install -r requirements.txt
```

### 3) Thiet lap database
- Chay file `schema` de tao database va bang.
- Cap nhat thong tin ket noi trong `.env`.

### 4) Migrate va tao du lieu mau
```powershell
python manage.py makemigrations
python manage.py migrate
python create_sample_data.py
```

### 5) Chay server
```powershell
python manage.py runserver
```

## Tai khoan mau
- Admin: `admin` / `admin@123`
- User mau: `student01` / `student123`

## URL tham khao
- Trang chu: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Danh sach sach: http://127.0.0.1:8000/library/books/

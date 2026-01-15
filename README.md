1️⃣ Tạo Project \& Virtual Environment

mkdir library\_system

cd library\_system

python -m venv venv



Kích hoạt virtual environment: => venv\\Scripts\\activate



2️⃣ Cài Đặt Packages

pip install -r requirements.txt



3️⃣ Tạo Django Project \& Apps

django-admin startproject library\_system .

python manage.py startapp accounts

python manage.py startapp library

python manage.py startapp borrowing

python manage.py startapp reviews

python manage.py startapp dashboard



4️⃣ Setup MySQL Database => Chạy file schema trong folder code.



5️⃣ Sửa biến môi trường trong file .env => Update username, pass,...



6️⃣ Migrate Database \& Tạo Admin

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser



7️⃣ Tạo Dữ Liệu Mẫu => Chạy python create\_sample\_data.py



8️⃣ Chạy Server => python manage.py runserver



🌐 URL

Trang chủ: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

Danh sách sách: http://127.0.0.1:8000/library/books/

...


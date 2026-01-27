# Manual Testing Checklist (Smoke Test)

## 1) Permissions
- Guest (not logged in)
  - Can view `/library/books/` and book detail
  - Cannot access admin pages (create/update/delete, category pages, dashboard, approvals)

- User (logged in, not admin)
  - Can create borrow request if book is available
  - Can see **My Requests**
  - Cannot access admin pages

- Admin (is_staff=True)
  - Can CRUD books (create/update/hide)
  - Can CRUD categories (create/update/hide) with rule: **cannot hide** if category has active books
  - Can approve/reject borrow requests
  - Can return books
  - Can approve/reject reviews

## 2) Book list search/filter/sort
- Search by title/author/ISBN
- Filter by category
- Sort by newest/title/popular
- Export CSV keeps current filters/sort

## 3) Category list search/filter/sort
- Search by name/description
- Filter by active/inactive
- Sort by name/book_count/newest

## 4) Borrowing workflow
- User: create request
- Admin: approve => create transaction + decrease `available_copies`
- Admin: return => increase `available_copies`

## 5) Review workflow
- User can only review after returning a book
- New review is `PENDING`
- Admin approves -> shown on book detail

## 6) Upload validation
- When creating/updating a Book, cover_image validates:
  - file type: JPG/PNG
  - size <= 5MB

## 7) Auth and notifications
- Login fail shows error message
- Login success shows success message
- Register success auto login and shows success message
- Logout shows info message

## 8) Automated tests (script/CLI)
PowerShell:
```powershell
if (Test-Path .\venv\Scripts\Activate.ps1) { . .\venv\Scripts\Activate.ps1 }
python manage.py test
```

CMD:
```cmd
call venv\Scripts\activate
python manage.py test
```

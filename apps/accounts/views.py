from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username","").strip()
        email = request.POST.get("email","").strip()
        password = request.POST.get("password","").strip()

        if not username or not password:
            messages.error(request, "Username và Password là bắt buộc.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username đã tồn tại.")
            return redirect("register")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Đăng ký thành công. Hãy đăng nhập.")
        return redirect("login")

    return render(request, "auth/register.html")

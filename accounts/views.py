from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm

def register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('home')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Chào mừng {user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng')
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Đã đăng xuất')
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
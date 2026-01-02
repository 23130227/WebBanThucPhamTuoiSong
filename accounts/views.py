from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth import update_session_auth_hash, login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from accounts.forms import RegisterForm, ProfileUpdateForm
from accounts.models import Profile


# Create your views here.
def register_view(request):
    context = {}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            context = {'form': form}
    return render(request, 'accounts/register.html', context)


def login_view(request):
    context = {}
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
        else:
            context = {'form': form}
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('index')


def forgot_password_view(request):
    context = {}
    return render(request, 'accounts/forgot-password.html', context)


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    success = False
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            success = True
            return redirect('profile')
    else:
        form = ProfileUpdateForm(user=request.user)

    context = {
        'form': form,
        'profile': profile,
        'success': success,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Giữ user đăng nhập sau khi đổi mật khẩu
            update_session_auth_hash(request, user)
            messages.success(request, 'Đổi mật khẩu thành công.')
            return redirect('password_change')
        messages.error(request, 'Đổi mật khẩu thất bại. Vui lòng kiểm tra lại thông tin.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/password-change.html', {'form': form})

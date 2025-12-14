from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth import update_session_auth_hash, login, authenticate, logout
from django.shortcuts import render, redirect

from accounts.forms import RegisterForm


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


def profile_view(request):
    context = {}
    return render(request, 'accounts/profile.html', context)


def password_change_view(request):
    context = {}
    return render(request, 'accounts/password-change.html', context)

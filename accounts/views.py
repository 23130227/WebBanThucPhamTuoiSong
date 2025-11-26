from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect


# Create your views here.
def register(request):
    context = {}
    return render(request, 'accounts/register.html', context)


def login(request):
    context = {}
    return render(request, 'accounts/login.html', context)


def forgot_password(request):
    context = {}
    return render(request, 'accounts/forgot-password.html', context)


def profile(request):
    context = {}
    return render(request, 'accounts/profile.html', context)


def password_change(request):
    context = {}
    return render(request, 'accounts/password-change.html', context)

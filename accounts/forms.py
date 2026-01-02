from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.Form):
    full_name = forms.CharField(required=False,label="Họ và tên",widget=forms.TextInput(attrs={"class": "form-control"}),)
    email = forms.EmailField(required=False,label="Email",widget=forms.EmailInput(attrs={"class": "form-control"}),)
    phone = forms.CharField(required=False,label="Số điện thoại",max_length=30,widget=forms.TextInput(attrs={"class": "form-control"}),)
    address = forms.CharField(required=False,label="Địa chỉ",widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),)
    bio = forms.CharField(required=False,label="Tiểu sử ngắn",widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),)
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["full_name"].initial = (user.get_full_name() or "").strip()
        self.fields["email"].initial = user.email or ""
        profile, _ = Profile.objects.get_or_create(user=user)
        self.profile = profile
        self.fields["phone"].initial = profile.phone
        self.fields["address"].initial = profile.address
        self.fields["bio"].initial = profile.bio

    def save(self):
        full_name = (self.cleaned_data.get("full_name") or "").strip()
        self.user.first_name = full_name
        self.user.email = self.cleaned_data.get("email") or ""
        self.user.save(update_fields=["first_name", "email"])
        self.profile.phone = self.cleaned_data.get("phone") or ""
        self.profile.address = self.cleaned_data.get("address") or ""
        self.profile.bio = self.cleaned_data.get("bio") or ""
        self.profile.save(update_fields=["phone", "address", "bio"])
        return self.profile

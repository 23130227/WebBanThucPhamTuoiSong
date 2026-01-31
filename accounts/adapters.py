from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Lấy thông tin từ Google
        data = sociallogin.account.extra_data

        # Cập nhật tên người dùng
        if 'name' in data:
            user.first_name = data.get('name', '')
            user.save()

        return user

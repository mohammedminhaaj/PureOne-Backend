from django.contrib import admin
from .models import UserOtp, LoginAttempt, User

# Register your models here.


@admin.register(UserOtp)
class UserOtpAdmin(admin.ModelAdmin):
    list_display = ["mobile", "otp", "expires_on", "attempts"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["mobile_number", "email", "username", "is_active"]


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ["user", "ip", "browser", "os",
                    "device", "time", "session_duration"]
    
    

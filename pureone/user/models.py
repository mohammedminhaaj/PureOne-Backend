
from typing import Iterable, Optional
from common.models import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class User(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=10, db_index = True, unique= True, error_messages={
            "unique": _("User already exists. Please use a different mobile number"),
        }, validators= [RegexValidator(r'^[0-9]*$', _("Invalid mobile number"))])
    email = models.EmailField("email address", null=True, blank= True, default=None, db_index=True)
    username = models.CharField(max_length=255, blank=True, null= True, default= None)
    is_active = models.BooleanField(default=True, help_text="is user account active?")
    is_staff = models.BooleanField(default=False, help_text="is user a Django admin?")

    password = models.CharField(_("password"), max_length=128, default=None, blank=True, null=True)  # type: ignore

    objects = UserManager()

    USERNAME_FIELD = "mobile_number"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.username = self.mobile_number
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.mobile_number}"

    class Meta:
        db_table = "auth_user"


class LoginAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(_("IP address"), unpack_ipv4=True)
    browser = models.CharField(max_length=50, default="Unknown")
    os = models.CharField(max_length=50, default="Unknown")
    device = models.CharField(max_length=50, default="Unknown")
    is_successful = models.BooleanField()
    time = models.DateTimeField(_("login attempted at"), auto_now_add=True)
    session_duration = models.SmallIntegerField()

    objects = models.Manager()

    def __str__(self) -> str:
        # returns as "2021-02-02T10:32:19+... -- Success: True -- Duration: 12 minute(s)"
        return f"{self.time} -- Success: {self.is_successful} -- Duration: {self.session_duration} minute(s)"

    class Meta:
        db_table = "login_attempt"
        get_latest_by = ["time"]
        verbose_name = "login attempt"
        verbose_name_plural = "login attempts"



class UserOtp(models.Model):
    mobile = models.CharField(max_length=10, verbose_name=_("Mobile Number"), db_index=True, unique=True)
    otp = models.CharField(max_length=256, verbose_name=_("OTP"))
    expires_on = models.DateTimeField(verbose_name=_("OTP Expires on"))
    attempts = models.PositiveSmallIntegerField(
        verbose_name=_("Attempts"), default=0)

    def __str__(self) -> str:
        return self.mobile

    class Meta:
        db_table = "user_otp"
        ordering = ["-id"]

from datetime import timedelta

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils.timezone import now
from django.conf import settings
from django.db.models.signals import post_save
from user.models import LoginAttempt, User
from django.http import HttpRequest


@receiver(user_logged_in)
def user_logged_in_callback(sender, request: HttpRequest, user: User, **kwargs):
    # if the user doesn't explicitly logout (session expiry), the `user_logged_out` signal is not sent
    # as a way to keep the database "sane", all previous incomplete records are updated to 60 mins session duration
    LoginAttempt.objects.filter(user=user, is_successful=True, session_duration=0).update(session_duration=60)
    LoginAttempt.objects.create(
        user=user,
        ip=request.META["REMOTE_ADDR"],
        browser=f"{request.user_agent.browser.family} {request.user_agent.browser.version_string}",
        os=f"{request.user_agent.os.family} {request.user_agent.os.version_string}",
        device=request.user_agent.device.family,
        is_successful=True,
        session_duration=0,
    )

    for s in Session.objects.all():
        if s.get_decoded().get("_auth_user_id") == str(user.id) and s.pk != request.session.session_key:
            s.delete()

""" # for k in cache.keys("django.contrib.sessions.cached_db*"):  # type: ignore
    #     if cache.get(k).get("_auth_user_id") == str(user.id) and k[33:] != request.session.session_key:
    #         cache.delete(k)"""


@receiver(user_logged_out)
def user_logged_out_callback(sender, user: User, **kwargs):
    attempt = LoginAttempt.objects.filter(user=user, is_successful=True).latest()
    attempt.session_duration = (now() - attempt.time).total_seconds() // 60
    attempt.save(update_fields=["session_duration"])


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials: dict[str, str], request: HttpRequest, **kwargs):
    try:
        user = User.objects.get(mobile_number=credentials.get("mobile_number"))
        LoginAttempt.objects.create(
            user=user,
            ip=request.META["REMOTE_ADDR"],
            browser=f"{request.user_agent.browser.family} {request.user_agent.browser.version_string}",
            os=f"{request.user_agent.os.family} {request.user_agent.os.version_string}",
            device=request.user_agent.device.family,
            is_successful=False,
            session_duration=0,
        )

        current_time = now()
        # temporarily block user accounts if wrong password provided 10 times within the last 24 hours
        if (
            LoginAttempt.objects.filter(
                user=user,
                time__gte=current_time - timedelta(days=1),
                time__lte=current_time,
                is_successful=False,
            ).count()
            >= 10
        ):
            user.is_active = False
            user.save(update_fields=["is_active"])
    except ObjectDoesNotExist:
        pass

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
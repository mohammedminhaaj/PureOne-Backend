from rest_framework.request import Request
from django.contrib.auth.signals import user_logged_in, user_login_failed
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import User, UserLocation
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from common.serializers.user_serializer import UserLocationSerializer


def auth_token_for_user(user: User, request: Request, response_message: str | None = None):
    user_location = UserLocation.objects.filter(user=user).order_by("id")
    user_location_serializer = UserLocationSerializer(
        user_location, many=True)
    token = Token.objects.get_or_create(user=user)
    response = Response(status=status.HTTP_200_OK)
    response.data = {"details": response_message,
                     "auth_token": token[0].key, "username": user.username, "mobile": user.mobile_number, "email": user.email, "saved_addresses": user_location_serializer.data}
    user_logged_in.send(sender=User, request=request, user=user)
    return response


def login_user(validated_data: dict, request: Request):
    email_number = validated_data.get("email_number")
    password = validated_data.get("password", None)
    try:
        user = User.objects.get(
            Q(mobile_number=email_number) | Q(email__iexact=email_number))
        authenticated = check_password(
            password, user.password) if password else True
        if not authenticated:
            user_login_failed.send(sender=User, credentials={
                "mobile_number": user.mobile_number}, request=request)
            raise AuthenticationFailed("Incorrect Password")
        elif not user.is_active:
            return Response(data={"details": "User account is not active at the moment"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return auth_token_for_user(user, request, "Login Successfull")

    except (User.DoesNotExist, AuthenticationFailed) as e:
        return Response(data={"details": "Invalid credentials. Please try again."}, status=status.HTTP_404_NOT_FOUND if type(e) == User.DoesNotExist else status.HTTP_400_BAD_REQUEST)

    except User.MultipleObjectsReturned:
        return Response(data={"details": "The email address provided is linked with multiple accounts. Please login using your mobile number instead."}, status=status.HTTP_404_NOT_FOUND)


def create_user(validated_data: dict, request: Request):
    mobile_number = validated_data.get("mobile_number")
    email = validated_data.get("email", None)
    password = validated_data.get("password")
    try:
        user = User.objects.create_user(
            mobile_number=mobile_number, email=email, password=password)
        return auth_token_for_user(user, request, "Account created successfully")
    except Exception as e:
        return Response(data={"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

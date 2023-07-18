from common.serializers.user_serializer import ForgotPasswordSerializer, CreateAccountSerializer, CredentialLoginSerializer, OtpLoginSerializer, VerifyOtpSerializer, UpdateProfileSerializer
from .models import UserOtp, User
from .helpers import create_user, login_user
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from os import getenv
from dotenv import load_dotenv
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.signals import user_logged_out, user_login_failed
from datetime import timedelta
from base64 import b64decode
from rest_framework import status
import requests
import random
import secrets
from common import constants

# Create your views here.


@api_view(["POST"])
def credential_login(request: Request):
    serializer = CredentialLoginSerializer(data=request.data)
    if serializer.is_valid():
        return login_user(serializer.validated_data, request)
    else:
        return Response(data = {"details": constants.FORM_ERROR, "errors": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_account(request: Request):
    serializer = CreateAccountSerializer(data=request.data)
    if serializer.is_valid():
        return create_user(serializer.validated_data, request)
    else:
        return Response(data = {"details": constants.FORM_ERROR, "errors": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def otp_login(request: Request):
    serializer = OtpLoginSerializer(data=request.data)
    if serializer.is_valid():
        load_dotenv()
        url = "https://www.fast2sms.com/dev/bulkV2"
        otp = random.randint(100000, 999999)
        mobile_number = serializer.validated_data.get('mobile_number')
        payload = f"variables_values={otp}&route=otp&numbers={mobile_number}"
        headers = {
            'authorization': b64decode(getenv("FAST2SMS_APIKEY")).decode(),
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache",
        }

        try:
            obj = UserOtp.objects.get(mobile=mobile_number)
            obj.otp = make_password(str(otp))
            obj.attempts = obj.attempts + 1 if now() <= obj.expires_on else 1
            obj.expires_on = now() + timedelta(minutes=30)
            obj.save(update_fields=["otp", "expires_on", "attempts"])
        except UserOtp.DoesNotExist:
            obj = UserOtp.objects.create(mobile=mobile_number, otp=make_password(
                str(otp)), expires_on=now() + timedelta(minutes=30))
        except Exception as e:
            return Response(data = {"details": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        if obj.attempts <= 5:
            response = requests.request(
                "POST", url, data=payload, headers=headers)
            return Response(data = response.json(), status=status.HTTP_200_OK)
        else:
            user_login_failed.send(sender=User, credentials={
                                   "mobile_number": obj.mobile}, request=request)
            return Response(data = {"details": "Maximum attempts exceeded. Please try again after some time"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data = {"details": constants.FORM_ERROR, "errors": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def verify_otp(request: Request):
    serializer = VerifyOtpSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(data = {"details": constants.FORM_ERROR, "errors": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

    mobile_number = serializer.validated_data.get('mobile_number')
    otp = serializer.validated_data.get('otp')
    try:
        obj = UserOtp.objects.get(mobile=mobile_number)
        verified = check_password(otp, obj.otp)
        if verified and obj.attempts <= 6:
            if obj.expires_on <= now():
                return Response(data = {"details": "the OTP provided is expired"}, status=status.HTTP_400_BAD_REQUEST)

            obj.attempts = 0
            obj.save(update_fields=["attempts"])

            response = login_user({"email_number": obj.mobile}, request)
            if response.status_code == status.HTTP_404_NOT_FOUND:
                response = create_user(
                    {"mobile_number": obj.mobile, "password": secrets.token_urlsafe(8)}, request)
            return response

        obj.attempts = obj.attempts + 1
        obj.save(update_fields=["attempts"])
        user_login_failed.send(sender=User, credentials={
                               "mobile_number": obj.mobile}, request=request)
        return Response(data = {"details": "Incorrect OTP" if obj.attempts <= 6 else "Maximum attempts exceeded. Please try again after some time"}, status = status.HTTP_400_BAD_REQUEST)

    except UserOtp.DoesNotExist:
        return Response(data = {"details": "Error while validating OTP"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(data = {"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
def forgot_password(request: Request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = User.objects.get(**serializer.validated_data)
            password = secrets.token_urlsafe(8)
            user.password = make_password(password)
            user.save(update_fields=["password"])
            print(password)
            """
            Email sending logic goes here
            """
            return Response(data = {"details": "Email sent successfully", "email": user.email}, status = status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(data = {"details": "Sorry, we didn't find any account linked to the given details"}, status = status.HTTP_404_NOT_FOUND)
    else:
        return Response(data = {"details": constants.FORM_ERROR, "errors": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request: Request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response(data = {"details": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    try: 
        auth_token = authorization_header.split(" ")[1]
        token = Token.objects.select_related("user").get(key = auth_token)
        user = token.user
        user_logged_out.send(sender=User, user=user)
        return Response(data = {"details": "User logged out successfully"}, status = status.HTTP_200_OK)
    except (IndexError, Token.DoesNotExist):
        return Response(data = {"details": "Invalid request header"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request: Request):
    serializer = UpdateProfileSerializer(data = request.data, instance=request.user)
    if serializer.is_valid():
        user = serializer.save()
        print(user.email, user.username)
        return Response(data = {"details": "Profile updated successfully"}, status = status.HTTP_200_OK)
    else:
        return Response(data = {"details": constants.FORM_ERROR, "errors": serializer.errors}, status = status.HTTP_400_BAD_REQUEST)
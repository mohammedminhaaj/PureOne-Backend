from rest_framework import serializers
from user.models import User

serializer_kwargs = {
    "credential": {
        "min_length": 6,
        "max_length": 128,
    },
    "mobile": {
        "max_length": 10,
        "min_length": 10,
    }
}

class CredentialLoginSerializer(serializers.Serializer):
    email_number = serializers.CharField(**serializer_kwargs["credential"])
    password = serializers.CharField(**serializer_kwargs["credential"])


class OtpLoginSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(**serializer_kwargs["mobile"])


class VerifyOtpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(**serializer_kwargs["mobile"])
    otp = serializers.CharField(max_length = 6, min_length = 6)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=None, min_length=None, allow_blank=False)
    mobile_number = serializers.CharField(**serializer_kwargs["mobile"])


class CreateAccountSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(**serializer_kwargs["credential"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["password"].required = True

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords don't match"})
        return super().validate(attrs)

    class Meta:
        model = User
        fields = ["mobile_number", "email", "password", "confirm_password"]

class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "mobile_number", "email"]

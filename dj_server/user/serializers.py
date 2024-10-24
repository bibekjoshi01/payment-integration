from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from .utils.generate_username import generate_unique_user_username

from .messages import (
    ACCOUNT_DISABLED,
    INVALID_CREDENTIALS,
    INVALID_PASSWORD,
    LOGIN_SUCCESS,
    PASSWORDS_NOT_MATCH,
    USER_ERRORS,
)
from .models import User


class UserSignUpSerializer(serializers.ModelSerializer):
    """Public User SignUp Serializer"""

    first_name = serializers.CharField(max_length=50, required=True)
    middle_name = serializers.CharField(max_length=50, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=True)
    phone_no = serializers.CharField(max_length=10, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=16,
        write_only=True,
        min_length=8,
        required=True,
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(
        max_length=16,
        write_only=True,
        min_length=8,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_no",
            "password",
            "confirm_password",
        ]

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": USER_ERRORS["EMAIL_EXISTS"]})

        if User.objects.filter(phone_no=attrs["phone_no"]).exists():
            raise serializers.ValidationError({"phone_no": USER_ERRORS["PHONE_EXISTS"]})

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": PASSWORDS_NOT_MATCH})

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        email = validated_data["email"]

        username = generate_unique_user_username(user_type="website_user")

        user_instance = User.objects.create_user(
            first_name=validated_data["first_name"].title(),
            middle_name=validated_data.get("middle_name", "").title(),
            last_name=validated_data["last_name"].title(),
            phone_no=validated_data["phone_no"],
            password=validated_data["password"],
            email=email,
            username=username,
        )
        user_instance.save()

        return user_instance


class UserLoginSerializer(serializers.ModelSerializer):
    """User Login Serializer"""

    persona = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["persona", "password"]

    def validate(self, attrs):
        persona = attrs.get("persona", None)
        password = attrs.pop("password", "")

        user = self.get_user(persona)
        self.check_password(user, password)
        self.check_user_status(user)

        # Update the last login datetime
        user.last_login = timezone.now()
        user.save()

        return {
            "message": LOGIN_SUCCESS,
            "status": "success",
            "id": user.id,
            "uuid": user.uuid,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "phone_no": user.phone_no,
            "is_superuser": user.is_superuser,
            "email": user.email,
            "tokens": user.tokens,
        }

    def get_user(self, persona):
        try:
            if "@" in persona:
                user = User.objects.get(email=persona)
            else:
                user = User.objects.get(username=persona)
        except User.DoesNotExist as err:
            raise serializers.ValidationError({"persona": INVALID_CREDENTIALS}) from err
        return user

    def check_password(self, user, password):
        if not user.check_password(password):
            raise serializers.ValidationError({"password": INVALID_PASSWORD})

    def check_user_status(self, user):
        if not user.is_active or user.is_archived:
            raise serializers.ValidationError({"persona": ACCOUNT_DISABLED})

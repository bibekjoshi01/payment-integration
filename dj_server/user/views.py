from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User
from .serializers import (
    UserLoginSerializer,
    UserSignUpSerializer,
)


class UserTokenRefreshView(TokenRefreshView):
    """Get AccessToken View"""

    authentication_classes = [JWTAuthentication]


class UserSignUpAPIView(generics.CreateAPIView):
    """
    User SignUp API View.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        return super().perform_create(serializer)


class UserLoginView(APIView):
    """User Login API View"""

    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

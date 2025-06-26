from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin
from django.contrib.auth import get_user_model, authenticate, login, logout
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, viewsets
from core.tasks import log_task
from .serializers import *


User = get_user_model()


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            log_task(f"Authenticated user {request.user.username} attempted to register. Logging out...", 'warning')
            logout(request)
            log_task(f"User {request.user.username} has been logged out", 'info')

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            log_task(f"User {user.username} registered successfully.", 'info')
        except Exception as e:
            log_task(f"Error during registration: {str(e)}", 'error')
            return Response({"errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # New user authorizating
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # JWT token generation
        refresh = RefreshToken.for_user(user)
        log_task(f"Tokens generated for user {user.username}: Refresh: {refresh}, Access: {refresh.access_token}", 'debug')

        user_serializer = UserSerializer(user)
        return Response({
            "message": "Registration successful!",
            "user": user_serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Check for active refresh token
            if OutstandingToken.objects.filter(user_id=user.id).exists() and not BlacklistedToken.objects.filter(token__user_id=user.id).exists():
                log_task(f"Authenticated user {user.username} attempted to log in.", 'warning')
                return Response({
                    'message': "User is already logged in.",
                    'access': str(RefreshToken.for_user(user).access_token),
                }, status=status.HTTP_200_OK)

            # Create new tokens if no active
            refresh = RefreshToken.for_user(user)
            log_task(f"Tokens generated for user {user.username}: Refresh: {refresh}, Access: {refresh.access_token}", 'debug')
            log_task(f"User {user.username} successfully logged in.", 'info')

            return Response({
                'message': "Successfully logged in!",
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        try:
            # Get the refresh token from the request body
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                log_task(f"User {request.user.username} did not provide a refresh token.", 'warning')
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_task(f"Refresh token for user {request.user.username} successfully blacklisted.", 'info')

            # Inform the client to clear the access token
            log_task(f"User {request.user.username} has been successfully loged out.", 'info')
            return Response({"detail": "Successfully logged out from account."}, status=status.HTTP_205_RESET_CONTENT)

        except (TokenError, InvalidToken):
            log_task(f"Logout failed for user {request.user.username} due to an invalid token: {str(e)}.", 'error')
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        log_task(f"User {self.request.user.username} changed the profile.", 'info')
        return self.request.user
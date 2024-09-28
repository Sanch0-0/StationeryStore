from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib import messages

from django.shortcuts import render, redirect
from .forms import UserCreationForm, LoginForm

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, LoginSerializer, UpdateProfileSerializer, UserSerializer



def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful!")
            login(request, user, backend='users.backends.EmailOrUsernameModelBackend')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'non_field_errors':
                        messages.error(request, error)
                    else:
                        if field == 'email':
                            messages.error(request, "Email: " + error)
                        elif field == 'username':
                            messages.error(request, "Username: " + error)
                        else:
                            messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'registration.html', context)


def login_view(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)

        if request.user.is_authenticated:
            messages.success(request, "You are already logged in.")

        elif form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)

            # Check if "Remember me" was selected
            if not request.POST.get('remember'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)  # 2 weeks

            messages.success(request, "Login successful!")
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


@login_required
def profile_view(request):
    user = request.user
    context = {
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'mobile_phone': user.mobile_phone,
        'country': user.country,
        'place_of_delivery': user.place_of_delivery,
        'postal_code': user.postal_code,
        'avatar': user.avatar.url if user.avatar else '',
    }
    return render(request, "profile.html", context)


@login_required
def update_profile(request):
    user = request.user

    if request.method == "POST":
        full_name = request.POST.get('full_name')
        mobile_phone = request.POST.get('mobile_phone')
        country = request.POST.get('country')
        place_of_delivery = request.POST.get('place_of_delivery')
        postal_code = request.POST.get('postal_code')
        avatar = request.FILES.get('avatar')  # Handle file uploads
        username = request.POST.get('username')

        user.full_name = full_name
        user.mobile_phone = mobile_phone
        user.country = country
        user.place_of_delivery = place_of_delivery
        user.postal_code = postal_code
        user.username = username

        if avatar:
            user.avatar = avatar

        user.save()

        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        if current_password and new_password:
            if check_password(current_password, user.password):
                user.set_password(new_password)  # Set the new password
                user.save()

                update_session_auth_hash(request, user)

                messages.success(request, "Password updated successfully!")
            else:
                messages.error(request, "Current password is incorrect!")

        messages.success(request, "Well done!")

    context = {
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'mobile_phone': user.mobile_phone,
        'country': user.country,
        'place_of_delivery': user.place_of_delivery,
        'postal_code': user.postal_code,
        'avatar': user.avatar.url if user.avatar else '',
    }

    return render(request, "profile.html", context)


def logout_view(request):

    return render(request=request, template_name="logout.html")


def logout_apply_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out.")
    else:
        messages.error(request, "You've already logged out.")
    return redirect('logout')





class UserViewSet(viewsets.ViewSet):

    # Register a new user
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully.", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Login user
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is not None:
                login(request, user)
                return Response({"message": "Login successful.", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)

    # Logout user
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

    # Update user profile
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "message": "Profile updated successfully!"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

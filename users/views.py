from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import User
from .forms import UserCreationForm, LoginForm


def register_view(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
        else:
            # Capture form errors and add to messages
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

    if request.method == "POST":
        # Manually handle profile updates
        full_name = request.POST.get('full_name')
        mobile_phone = request.POST.get('mobile_phone')
        country = request.POST.get('country')
        place_of_delivery = request.POST.get('place_of_delivery')
        postal_code = request.POST.get('postal_code')
        avatar = request.FILES.get('avatar')  # Handle file uploads
        username = request.POST.get('username')

        # Update profile fields
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

        # Check if the current password is correct
        if current_password and new_password:
            if check_password(current_password, user.password):
                user.set_password(new_password)  # Set the new password
                user.save()

                # Keep the user logged in after password change
                update_session_auth_hash(request, user)

                messages.success(request, "Password updated successfully!")
            else:
                messages.error(request, "Current password is incorrect!")

        return redirect('profile')

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

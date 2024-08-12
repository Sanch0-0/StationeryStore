from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from .models import User
from .forms import UserCreationForm, LoginForm, ProfileUpdateForm


def register_view(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'non_field_errors':
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field.capitalize()}: {error}")

    context = {
        'form': form,
    }

    return render(request, 'registration.html', context)


def login_view(request):

    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if request.user.is_authenticated:
            messages.success(request, "You are already logged in.")

        elif form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(
                request=request,
                email=email,
                password=password
            )

            if user is not None:
                login(request=request, user=user)


                # Check if "Remember me" was selected
                if not request.POST.get('remember'):
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)  # 2 weeks

                messages.success(request, "Login successful!")
            else:
                if not User.objects.filter(email=email).exists():
                    messages.error(request, "This email is not registered.")
                else:
                    messages.error(request, "Invalid email or password.")
        else:
            # Manually add errors for specific fields
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def update_view(request):

    form = ProfileUpdateForm(
        data=request.POST, files=request.FILES, instance=request.user)

    if form.is_valid():
        form.save()
    return redirect("profile")


def profile_view(request):

    form = ProfileUpdateForm(instance=request.user)

    context = {
        "form": form
    }

    return render(request=request, template_name="profile.html", context=context)


def logout_view(request):

    return render(request=request, template_name="logout.html")


def logout_apply_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out.")
    else:
        messages.error(request, "You've already logged out.")
    return redirect('logout')

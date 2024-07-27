from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from .models import User
from .forms import UserCreationForm, LoginForm, ProfileUpdateForm


def register_view(request):

    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect()

    context = {
        'form': form,
    }

    return render(request=request, template_name='registration.html', context=context)


def loigin_view(request):

    form = LoginForm()
    message = ''
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                request=request,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request=request, user=user)
                return redirect()
            message = "Invalid data"

    context = {
        'form': form,
        'message': message,
    }

    return render(request=request, template_name='login.html', context=context)


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

    logout(request)
    return redirect('login')

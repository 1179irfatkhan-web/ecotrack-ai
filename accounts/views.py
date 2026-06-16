from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegisterForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to EcoTrack AI, {user.username}! Your account has been registered successfully.")
            return redirect('/dashboard/')
    else:
        form = RegisterForm()

    return render(
        request,
        'register.html',
        {
            'form': form
        }
    )
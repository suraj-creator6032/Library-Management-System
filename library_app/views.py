from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import UserProfile


def member_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'library_app/login.html')


@login_required
def dashboard(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        logout(request)
        messages.error(
            request,
            'Your account is not linked to a library membership.'
        )
        return redirect('member_login')

    return render(
        request,
        'library_app/dashboard.html',
        {'profile': profile, 'member': profile.member}
    )


@login_required
def member_logout(request):
    logout(request)
    return redirect('member_login')
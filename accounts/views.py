from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from tribes.models import Profile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('landing')
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'landing'))
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email.')
    return render(request, 'accounts/login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('landing')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
        else:
            username = email.split('@')[0]
            base = username
            i = 1
            while User.objects.filter(username=username).exists():
                username = f'{base}{i}'
                i += 1
            first = name.split()[0] if name else ''
            last = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first, last_name=last)
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('explore')
    return render(request, 'accounts/signup.html')


def logout_view(request):
    logout(request)
    return redirect('landing')

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to LegitEdu, {user.username}!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=400)
        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({'message': 'Account created successfully'}, status=201)

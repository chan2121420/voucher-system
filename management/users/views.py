from . models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from . forms import userCreationForm, userForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

def userLogin(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username = username, password = password)

            if user is not None:    
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    return render(request, 'accounts/login.html', {'form':form})

def userCreation(request):
    form = userCreationForm()
    if request.method == 'POST':
        form = userCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful." )
            return redirect('users')
    return render(request, 'accounts/create_user.html', {'form':form})

def users(request):
    user = User.objects.all()
    return render(request, 'accounts/users.html', {'users':user})

def userDetail(request, pk):
    try:
        user = User.objects.get(pk = pk)
    except:
        return render(request, '404.html')
    return render(request, 'accounts/user_detail.html', {'user':user})

def user(request, pk):
    try:
        user = User.objects.get(pk = pk)
    except:
        return render(request, '404.html')

    form = userForm(request.POST or None, instance = user)
    if form.is_valid():
        form.save()
        messages.success(request, "saved successfully." )
        return redirect('users:users')
    return render(request, 'accounts/user.html', {'form':form})

def userDelete(request, pk):
    try:
        user = User.objects.get(pk = pk)
    except:
        return render(request, '404.html')
    user.delete()
    messages.success(request, "successfully deleted" )
    return redirect('users:users')

def userLogout(request):
    logout(request)
    return redirect('users:login')

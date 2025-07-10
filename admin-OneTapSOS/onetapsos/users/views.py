from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile


# Create your views here.
def login_view(request):
    return render(request, 'users/login.html')



#Register
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            # Create the Profile and save the phone number
            profile = Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number']
            )
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')  # Change to your login URL name
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})



def user_list(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})

def user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/view.html', {'user': user})

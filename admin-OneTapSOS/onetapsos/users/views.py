from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

# Create your views here.
def login_view(request):
    return render(request, 'users/login.html')

def register_view(request):
    return render(request, 'users/register.html')

def user_list(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})

def user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/view.html', {'user': user})

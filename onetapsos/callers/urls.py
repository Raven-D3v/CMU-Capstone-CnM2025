from django.urls import path
from .views import CallerRegisterView, CallerLoginView

urlpatterns = [
    path('register/', CallerRegisterView.as_view(), name='caller-register'),
    path('login/', CallerLoginView.as_view(), name='caller-login'),
]
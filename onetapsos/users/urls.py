from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('list/', views.user_list, name='user_list'),
    path('view/<int:user_id>/', views.user_view, name='user_view'),
]


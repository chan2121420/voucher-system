from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('users/', views.users, name='users'),
    path('logout/', views.userLogout, name='logout'),
    path('login/', views.userLogin, name='login'),
    path('user/<int:pk>/', views.user, name='user'),
    path('createUser/', views.userCreation, name='createUser'),
    path('userDelete/<int:pk>/', views.userDelete, name='userDelete'),
    path('userDetail/<int:pk>/', views.userDetail, name='userDetail'),
]

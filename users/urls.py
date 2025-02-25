from django.urls import path, include
from . import views
from . api import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'users'

urlpatterns = [
    path('users/', views.users, name='users'),
    path('logout/', views.userLogout, name='logout'),
    path('login/', views.userLogin, name='login'),
    path('user/<int:pk>/', views.user, name='user'),
    path('createUser/', views.userCreation, name='createUser'),
    path('userDelete/<int:pk>/', views.userDelete, name='userDelete'),
    path('userDetail/<int:pk>/', views.userDetail, name='userDetail'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]

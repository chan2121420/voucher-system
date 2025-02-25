from django.urls import path, include
from . import views
from . api import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/v1/users', UserViewSet, basename='user')

app_name = 'users'

urlpatterns = [
    path('users/', views.users, name='users'),
    path('logout/', views.userLogout, name='logout'),
    path('login/', views.userLogin, name='login'),
    path('user/<int:pk>/', views.user, name='user'),
    path('createUser/', views.userCreation, name='createUser'),
    path('userDelete/<int:pk>/', views.userDelete, name='userDelete'),
    path('userDetail/<int:pk>/', views.userDetail, name='userDetail'),

    path('api/v1/register/', RegisterView.as_view(), name='api_register'),
    path('api/v1/login/', LoginView.as_view(), name='api_login'),
    path('api/v1/logout/', LogoutView.as_view(), name='api_logout'),
    path('', include(router.urls)),
]

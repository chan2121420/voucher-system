from . import views
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('users/', include('users.urls', namespace='users')),
    path('vouchers/', include('vouchers.urls', namespace='vouchers')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

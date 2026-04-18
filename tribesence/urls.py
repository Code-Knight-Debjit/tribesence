from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('tribes/', include('tribes.urls')),
    path('accounts/', include('accounts.urls')),
]

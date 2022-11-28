from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('msa/', include('Msa.urls')),
    path('asang/', include('asang.urls')),
]

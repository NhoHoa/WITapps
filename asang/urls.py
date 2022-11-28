from django.urls import path
from .views import AsangView

app_name ='asang'
urlpatterns = [
    path('',AsangView.as_view(), name = 'AOImachine'),
]

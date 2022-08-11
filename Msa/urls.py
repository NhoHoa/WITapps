from django.urls import path
from .views import MsaView

app_name ='Msa'
urlpatterns = [
    path('',MsaView.as_view(), name = 'getdata'),
]

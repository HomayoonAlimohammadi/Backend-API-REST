from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [ 
    path('create/', views.CreateUserAPIView.as_view(), name='create'),
]
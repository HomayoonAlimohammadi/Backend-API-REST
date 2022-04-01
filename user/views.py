from rest_framework import generics
from .serializers import UserSerializer


class CreateUserAPIView(generics.CreateAPIView):
    
    serializer_class = UserSerializer

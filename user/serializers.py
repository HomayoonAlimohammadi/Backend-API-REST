from rest_framework import serializers

from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    '''
    Serializer for the user objects
    '''
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {'min_length': 5, 'write_only': True}
        }

    def create(self, validated_data):
        '''
        Create & return user with valid credentials and encrypted password''' 
        return get_user_model().objects.create_user(**validated_data)
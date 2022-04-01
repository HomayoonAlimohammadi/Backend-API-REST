from rest_framework import serializers

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

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


class TokenSerializer(serializers.Serializer):
    '''
    Serializer for Auth Token
    '''
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        '''
        Validating email and password for auth token
        '''
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to validate credentials.')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
        
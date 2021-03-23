from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password1': "password field dont match !"})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        if not 'first_name' in validated_data:
            user.first_name = ""
        else:
            user.first_name = validated_data['first_name']
        if not 'last_name' in validated_data:
            user.last_name = ""
        else:
            user.last_name = validated_data['last_name']
        user.set_password(validated_data['password1'])
        profile = Profile.objects.create(user=user)
    
        profile.save()
        user.save()

        return user

class UserLoginSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['tokens'] = {'refresh': str(refresh), "access": str(refresh.access_token)}
        data['user'] = {'key': self.user.profile.key, 'username': self.user.username, 'email': self.user.email, 'first_name': self.user.first_name, 'last_name': self.user.last_name, 'image': self.user.profile.image.url}


        return data

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email

from .models import Profile
from .serializers import RegisterSerializer, UserLoginSerializer

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase
from rest_framework_simplejwt.tokens import RefreshToken

import time
import random

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, key, format=None):
        user = request.user
        if request.data['password1'] != request.data['password2']:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'password1': "password fields dont match !"})
        if not user.check_password(request.data['old_password']):
            return Response(status=status.HTTP_403_FORBIDDEN, data={"old_password": "old password is not correct !"})
        if user.profile.key != key:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"authorize": "You dont have permission for this user !"})
        try:
            validate_password(request.data['password1'], user=user)
        except ValidationError as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": {"password": ex}})

        instance = User.objects.get(profile__key=key)
        instance.set_password(request.data['password1'])
        instance.save()
        return Response(status=status.HTTP_200_OK, data={"detail": "password changed"})


class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, key, format=None):
        user = request.user
        if user.profile.key != key:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"authorize": "you dont have permission for this user !"})
        if len(request.data) == 0:
              return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "no field modified"})
        instance = User.objects.get(profile__key=key)
        if 'first_name' in request.data:
            instance.first_name = request.data['first_name']
        if 'last_name' in request.data:
            instance.last_name = request.data['last_name']
        if 'email' in request.data:
            if User.objects.exclude(profile__key=user.profile.key).filter(email=request.data['email']).exists():
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={"email": "this email is already in use !"})
            try:
                validate_email(request.data['email'])
            except ValidationError as ex:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": {"email": ex}})
            instance.email = request.data['email']
        if 'username' in request.data:
            if User.objects.exclude(profile__key=user.profile.key).filter(username=request.data['username']).exists():
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={"username": "this username is not available !"})
            instance.username = request.data['username']
        instance.save()
        return Response(status=status.HTTP_200_OK, data={"detail": "updated"})


class UserLoginView(TokenViewBase):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )

class UpdateUserImageView(generics.UpdateAPIView):
    parser_classes = (MultiPartParser, )
    permission_classes = (IsAuthenticated,)
    def put(self, request, key, format=None):
        user = request.user
        if user.profile.key != key:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={
                'detail':{
                    "authorize": "you dont have permission for this user !"
                    }
                })
        if 'image' in request.data:
            profile = get_object_or_404(Profile, key=key)
            profile.image = request.data['image']
            profile.user = user
            profile.save()
            return Response(status=status.HTTP_200_OK, data={"detail": 'modified'})
        else:
            return Response(status=status.HTTP_404_NOT_FOUND,data={'detail': {'not-valid': 'the image field data is missing'}})

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT, data={'detail': "logged out"})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "refresh_token is not valid"})

class DeleteProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    def delete(self, request, key, format=None):
        user = request.user
        if user.profile.key != key:
            return Response(data={"detail": "unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        if not 'password' in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'password-required'})
        if not user.check_password(request.data['password']):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': "password-incorrect"})
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_200_OK, data={"detail": "deleted"})

class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        if 'email' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': {'email': 'required'}})
        try:
            validate_email(request.data['email'])
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": {"email": "enter a valid email address!"}})
        try:
            user = User.objects.get(email=request.data["email"])
        except User.DoesNotExist:
            time.sleep(3)
            return Response(status=status.HTTP_200_OK, data={'detail': "sent"})
        mail_subject = 'Reset Your Password'
        server_code = random.randint(10000, 999999)
        name = "user"
        if not user.first_name == "":
            name = user.first_name
        message = 'Hi {0},\nthis is your email confirmation code:\n{1}'.format(name, server_code)
        to_email = user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email]).send()
        request.session['code'] = server_code
        request.session['user'] = user.username
        return Response(status=status.HTTP_200_OK, data={'detail': "sent"})

class ValidateConfirmationCodeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        if not request.session.has_key('code') and request.session.has_key('user'):
            return Response(status=status.HTTP_404_NOT_FOUND, data={'detail': 'session-not-found'})
        if not 'code' in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': {"code": "required"}})
        if not int(request.data['code']) == int(request.session.get('code')):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'wrong-code'})
        return Response(status=status.HTTP_200_OK, data={'key': get_object_or_404(User, username=request.session['user']).profile.key})
class ResetPasswordView(APIView):
    """ """
    permission_classes = (AllowAny,)

    def put(self, request, key, format=None):
        user = get_object_or_404(User, username=request.session.get('user'))
        if user.profile.key != key:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "unauthorized"})
        if not 'password' and 'again' in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': {"password": "required", 'again': 'required'}})
        if request.data["password"] != request.data['again']:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': {"password": 'not-matched'}})
        try:
            validate_password(request.data['password'], user=user)
        except ValidationError as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": {"password": ex}})

        user.set_password(request.data['password'])
        user.save()
        request.session.flush()
        return Response(status=status.HTTP_200_OK, data={'detail': 'done'})

from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import GroupSerializer
from .models import Group, Movie
from config.settings import MOVIE_PER_USER
class CreateGroup(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def post(self, request, format=None):
		if not "name" in request.data:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "name is not in request."})
		if Group.objects.filter(name=request.data['name']).exists():
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "group name already exisit."})
		group = Group.objects.create(
			name=request.data['name'],
			admin=request.user
		)
		serializer = GroupSerializer(instance=group)
		return Response(status=status.HTTP_201_CREATED, data={"detail": "group '{0}' added.".format(group.name), "data": serializer.data})

# class CreateMovie(APIView):
# 	permission_classes = (permissions.IsAuthenticated, )

# 	def post(self, request, format=None):
# 		if 
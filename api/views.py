from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import GroupSerializer, MovieSerializer, GroupMemberSerializer
from .models import Group, Movie
from .utils import invite_code
from customauth.models import Profile
from config.settings import MOVIE_PER_USER
import random
from itertools import chain 


def all_movies_in_group(key):
	group = get_object_or_404(Group, key=key)
	all_profiles = group.profile_set.all()
	all_group_movies = []
	for profile in all_profiles:
		user_movies = profile.user.movie.filter(watched=False).values_list("key", flat=True)
		all_group_movies.append(list(user_movies))
	all_group_movie_keys = list(chain.from_iterable(all_group_movies))
	return all_group_movie_keys

def have_permission_for_group(group_key, user):
	if not user.profile.group.filter(key=group_key).exists():
		return False
	return True


def is_admin_user(group_key, user):
	group = get_object_or_404(Group, key=group_key)
	if group.admin != user:
		return False
	return True


class CreateGroupView(APIView):
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
		request.user.profile.group.add(group)
		serializer = GroupSerializer(instance=group)
		return Response(status=status.HTTP_201_CREATED, data={"detail": "group '{0}' added.".format(group.name), "data": serializer.data})

class EditAndDeleteGroupView(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, group_key, format=None):
		user = request.user
		if not is_admin_user(group_key, user):
			return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission to perform this action."})
		if len(request.data) == 0:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "no new data provided."})
		group = get_object_or_404(Group, key=group_key)
		if "name" in request.data:
			group.name = request.data["name"]
			group.save()

		if "users" in request.data:
			users = request.data["users"]
			for user in users:
				profile = get_object_or_404(Profile, key=user)
				profile.group.remove(group)
		return Response(status=status.HTTP_200_OK)


	def delete(self, request, group_key, format=None):
		user = request.user
		if not is_admin_user(group_key, user):
			return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission to perform this action."})
		group = get_object_or_404(Group, key=group_key)
		group.delete()
		return Response(status=status.HTTP_200_OK, data={"detail": "group '{0}' deleted.".format(group.name)})


class CreateAndGetMovieView(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def post(self, request, format=None):

		user = request.user
		user_movies_count = Movie.objects.filter(user=user).count()
		if user_movies_count >= MOVIE_PER_USER:
			return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data={"detail": "you reached the limit of adding movie. limit:{0}".format(MOVIE_PER_USER)})
		if not "name" in request.data:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "'name' is required."})
		if Movie.objects.filter(user=user, name=request.data["name"]).exists():
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "movie with this name already exists."})
		movie = Movie.objects.create(name=request.data["name"], user=user)
		if "description" in request.data:
			movie.description = request.data["description"]
		if "year" in request.data:
			movie.year = request.data["year"]
		if "imdb_rate" in request.data:
			movie.imdb_rate = request.data["imdb_rate"]
		if "download_link" in request.data:
			movie.download_link = request.data["download_link"]
		if "poster_link" in request.data:
			movie.poster_link = request.data["poster_link"]
		if "review" in request.data:
			movie.review = request.data["review"]

		movie.save()
		return Response(status=status.HTTP_201_CREATED, data={"detail": "movie '{0}' created".format(movie.name)})

	def get(self, request, format=None):
		user = request.user
		movies = user.movie.all()
		serializer = MovieSerializer(instance=movies, many=True)
		return Response(status=status.HTTP_200_OK, data=serializer.data)


class EditAndDeleteMovieView(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, key, format=None):
		user = request.user
		movie = get_object_or_404(Movie, key=key)
		if movie.user != user:
			return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "you dont have permission for this movie."})
		if len(request.data) == 0:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "no new data provided."})
		if "name" in request.data:
			movie.name = request.data["name"]
		if "description" in request.data:
			movie.description = request.data["description"]
		if "year" in request.data:
			movie.year = request.data["year"]
		if "imdb_rate" in request.data:
			movie.imdb_rate = request.data["imdb_rate"]
		if "watched" in request.data:
			movie.watched = request.data["watched"]
		if "download_link" in request.data:
			movie.download_link = request.data["download_link"]
		if "poster_link" in request.data:
			movie.poster_link = request.data["poster_link"]
		if "review" in request.data:
			movie.review = request.data["review"]
		movie.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "updated"})
		

	def delete(self, request, key, format=None):
		user = request.user
		movie = get_object_or_404(Movie, key=key)
		if movie.user != user:
			return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission for this movie."})
		movie.delete()
		return Response(status=status.HTTP_200_OK, data={"detail": "movie '{0}' deleted".format(movie.name)})



class GetRandomMovieView(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, key, format=None):
		user = request.user
		group = get_object_or_404(Group, key=key)

		if not have_permission_for_group(key, user):
			return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "you dont have permission for this group."})
		all_group_movie_keys = all_movies_in_group(key)
		selected_movie_key = random.choice(all_group_movie_keys)
		movie = get_object_or_404(Movie, key=selected_movie_key)
		serializer = MovieSerializer(instance=movie)
		return Response(status=status.HTTP_200_OK, data=serializer.data)

class SubmitMovieView(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, group, movie, format=None):
		user = request.user
		group_obj = get_object_or_404(Group, key=group)
		if not have_permission_for_group(group, user):
			return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "you dont have permission for this group."})
		all_movies_keys = all_movies_in_group(group)
		if not movie in all_movies_keys:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "movie not found as one of the group members movie."})
		movie = get_object_or_404(Movie, key=movie)
		group_obj.movie_of_the_week = movie
		group_obj.save()
		movie.watched = True
		movie.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "'{0}' selected as movie of the week.".format(movie.name)})

class AllUserGroups(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, format=None):
		user = request.user
		groups = user.profile.group.all()
		serializer = GroupSerializer(instance=groups, many=True)
		return Response(status=status.HTTP_200_OK, data={"data": serializer.data})

class AllGroupMembersProfile(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, group_key, format=None):
		user = request.user
		if not have_permission_for_group(group_key, user):
			return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "you dont have permission for this group."})
		group = get_object_or_404(Group, key=group_key)
		all_members = Profile.objects.filter(group=group)
		group_serializer = GroupMemberSerializer(instance=all_members, many=True)
		return Response(status=status.HTTP_200_OK, data=group_serializer.data)


class GenerateInviteCode(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, group_key, format=None):
		user = request.user
		if not is_admin_user(group_key, user):
			return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission to perform this action."})
		group = get_object_or_404(Group, key=group_key)
		group.invite_code = invite_code()
		group.save()
		return Response(status=status.HTTP_200_OK, data={"code": group.invite_code})

class JoinGroup(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, invite_code, format=None):
		user = request.user
		if not Group.objects.filter(invite_code=invite_code).exists():
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "requested group does not exist, please inform the admin to generate a new key."})
		group = get_object_or_404(Group, invite_code=invite_code)
		user.profile.group.add(group)
		return Response(status=status.HTTP_200_OK, data={"detail": "you are now a member of group '{0}'.".format(group.name)})

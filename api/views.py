from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import (
	GroupSerializer, MovieSerializer, GroupMemberSerializer
	)
from .models import Group, Movie
from .views_utils import (
	all_movies_in_group, have_permission_for_group, is_admin_user
	)
from .utils import invite_code
from customauth.models import Profile
from config.settings import MOVIE_PER_USER
import random


class CreateGroupView(APIView):
	""" create group allowed for every authenticated user. get field ['name']. """
	permission_classes = (permissions.IsAuthenticated, )

	def post(self, request, format=None):
		"""
			Attributes
			----------
			group -> api.models.Group(object) : contain group object made with user data
			serializer -> api.serializers.GroupSerializer(object) : contain serialized data of 'group' object

			Responses
			----------
			400 -> key="detail", value="name is not in request." : if field 'name' not in request.data
			400 -> key="detail", value="group name already exisit." : if group name already exists
			201 -> [key="detail", value="group '{0}' added." : {0} is group given name], [key="data", value=contain serialized data]

			Input Types
			----------

			Required
			request.data["name"] -> String

			Optional
			request.data["image"] -> Image

		"""

		if "name" not in request.data:
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "name is not in request."})

		if Group.objects.filter(name=request.data['name']).exists():
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "group name already exisit."})

		group = Group.objects.create(
			name=request.data['name'],
			admin=request.user
		)
		if "image" in request.data:
			group.image = request.data["image"]
			group.save()
		request.user.profile.group.add(group)

		serializer = GroupSerializer(instance=group)
		return Response(
			status=status.HTTP_201_CREATED,
			data={"detail": "group '{0}' added.".format(group.name), "data": serializer.data})


class EditAndDeleteGroupView(APIView):
	""" admin only with put 'name' and 'users' , users is an array of users key. and group key should include in url. """
	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, group_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			group -> api.models.Group(object) : contain group object which key is group_key

			Responses
			----------
			403 -> key="detail", value="you dont have permission to perform this action." : if user not group admin
			400 -> key="detail", value="no new data provided." : if no field in request.data
			404 -> key="detail", value="Not found." : if the given 'group_key' in the url is not refer to a Group object
			200 -> ket="detail", value="modified"

			Input Types
			----------
			request.data["name"] -> String
			request.data["image"] -> Image
			request.data["users"] -> Array (of user 'key's)
			group_key -> String : in url

		"""

		user = request.user
		if not is_admin_user(group_key, user):
			return Response(
				status=status.HTTP_403_FORBIDDEN,
				data={"detail": "you dont have permission to perform this action."})

		if len(request.data) == 0:
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "no new data provided."})

		group = get_object_or_404(Group, key=group_key)
		if "name" in request.data:
			group.name = request.data["name"]
		if "image" in request.data:
			group.image = request.data["image"]
		group.save()

		if "users" in request.data:
			users = request.data["users"]
			for user in users:
				profile = get_object_or_404(Profile, key=user)
				profile.group.remove(group)
		return Response(status=status.HTTP_200_OK, data={"detail": "modified"})

	def delete(self, request, group_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			group -> api.models.Group(object) : contain group object which key is group_key

			Responses
			----------
			403 -> key="detail", value="you dont have permission to perform this action." : if user not group admin
			404 -> key="detail", value="Not found." : if the given 'group_key' in the url is not refer to a Group object
			200 -> key="detail", value="group '{0}' deleted." : {0} is group name

			Input Types
			----------
			group_key -> String : in url

		"""

		user = request.user
		if not is_admin_user(group_key, user):
			return Response(
				status=status.HTTP_403_FORBIDDEN,
				data={"detail": "you dont have permission to perform this action."})

		group = get_object_or_404(Group, key=group_key)
		group.delete()
		return Response(
			status=status.HTTP_200_OK,
			data={"detail": "group '{0}' deleted.".format(group.name)})


class CreateAndGetMovieView(APIView):
	""" on post add movie can include fields ["name", "description", "year", "imdb_rate", "download_link", "poster_link", "review"] and name is required. on get return all movies of user. """
	permission_classes = (permissions.IsAuthenticated, )

	def post(self, request, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			user_movies_count -> int : count all movies of the user
			movie -> api.models.Movie(object) : contain movie object that get created with user data

			Responses
			----------
			406 -> key="detail", value="you reached the limit of adding movie. limit:{0}" {0} is limit that set in projects settings
			400 -> key="detail", value="'name' is required." : if not field 'name' in request.data
			400 -> key="detail", value="movie with this name already exists." : if movie name included in user movies
			201 -> key="detail", value="movie '{0}' created" : {0} is given movie name

			Input Types
			----------

			Required
			request.data["name"] -> String

			Optional
			request.data["description"] -> String
			request.data["year"] -> int
			request.data["imdb_rate"] -> Float
			request.data["download_link"] -> String
			request.data["poster_link"] -> String
			request.data["review"] -> String

			TODO:Frontend: check for poster_link and download_link to be valid url

		"""

		user = request.user
		user_movies_count = Movie.objects.filter(user=user).count()
		if user_movies_count >= MOVIE_PER_USER:
			return Response(
				status=status.HTTP_406_NOT_ACCEPTABLE,
				data={"detail": "you reached the limit of adding movie. limit:{0}".format(MOVIE_PER_USER)})

		if "name" not in request.data:
			return Response(
				status=status.HTTP_400_BAD_REQUEST, data={"detail": "'name' is required."})

		if Movie.objects.filter(user=user, name=request.data["name"]).exists():
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "movie with this name already exists."})

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
		return Response(
			status=status.HTTP_201_CREATED,
			data={"detail": "movie '{0}' created".format(movie.name)})

	def get(self, request, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			movies -> django.db.models.query.QuerySet(object) : contain all user movies
			serializer -> api.serializers.MovieSerializer(object) : contain serialized data of 'movies' queryset

			Responses
			----------
			200 -> serialized movies data in json

		"""

		user = request.user
		movies = user.movie.all()
		serializer = MovieSerializer(instance=movies, many=True)
		return Response(status=status.HTTP_200_OK, data=serializer.data)


class EditAndDeleteMovieView(APIView):
	""" for both edit and delete should include movie key. put can include fields ["name", "description", "year", "imdb_rate", "watched", "download_link", "poster_link", "review"] """
	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			movie -> api.models.Movie(object) : contain movie object that key passed to url

			Responses
			----------
			404 -> key="detail", value="Not found." : if the given 'key' in the url is not refer to a movie object
			401 -> key="detail", value="you dont have permission for this movie." : if user requesting dont match the movie owner
			400 -> key="detail", value="no new data provided." : if there is no field in request.data
			200 -> key="detail", value="updated"

			Input Types
			----------
			Required
			key -> String : in url

			Optional : at least one of this should be in request.data
			request.data["name"] -> String
			request.data["description"] -> String
			request.data["year"] -> int
			request.data["imdb_rate"] -> float
			request.data["watched"] -> bool
			request.data["download_link"] -> String
			request.data["poster_link"] -> String
			request.data["review"] -> String

		"""

		user = request.user
		movie = get_object_or_404(Movie, key=key)
		if movie.user != user:
			return Response(
				status=status.HTTP_401_UNAUTHORIZED,
				data={"detail": "you dont have permission for this movie."})

		if len(request.data) == 0:
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "no new data provided."})

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
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user
			 which sending the request
			movie -> api.models.Movie(object) : contain movie object that key passed to
			 url

			Responses
			----------
			404 -> key="detail", value="Not found." : if the given 'key' in the url is not refer to a movie object
			403 -> key="detail", value="you dont have permission for this movie." : if authenticated user is not movie owner
			200 -> key="detail", value="movie '{0}' deleted." : {0} can be movie name

			Input Types
			----------
			key -> String : in the url
		"""

		user = request.user
		movie = get_object_or_404(Movie, key=key)
		if movie.user != user:
			return Response(
				status=status.HTTP_403_FORBIDDEN,
				data={"detail": "you dont have permission for this movie."})

		movie.delete()
		return Response(
			status=status.HTTP_200_OK,
			data={"detail": "movie '{0}' deleted.".format(movie.name)})


class GetRandomMovieView(APIView):
	""" every user that is group member can get this. should include group key in url. """
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			all_group_movie_keys -> list : store value of all_movies_in_group function
			selected_movie_key -> str : a random movie key choosed from all_group_movie_keys list
			movie -> api.models.Movie(object) : contain Movie object , with selected_movie_key key
			serializer -> api.serializers.MovieSerializer(object) : contain serialized data of 'movie'

			Responses
			----------
			404 -> key="detail", value="Not found." : given group key object not found
			401 -> key="detail", value="you dont have permission for this group." : if user not a member of group
			404 -> key="detail", value="Not found." : if choosed movie as random corrupt or delete
			200 -> return serialized data of the choosed movie

			Input Types
			----------
			key -> String : in the url
		"""

		user = request.user

		if not have_permission_for_group(key, user):
			return Response(
				status=status.HTTP_401_UNAUTHORIZED,
				data={"detail": "you dont have permission for this group."})

		all_group_movie_keys = all_movies_in_group(key)
		selected_movie_key = random.choice(all_group_movie_keys)
		movie = get_object_or_404(Movie, key=selected_movie_key)
		serializer = MovieSerializer(instance=movie)
		return Response(status=status.HTTP_200_OK, data=serializer.data)


class SubmitMovieView(APIView):
	""" every user that is a group member can submit a movie. should pass group key and movie key in url. """
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, group, movie, format=None):
		"""
			Attributes
			----------
			Responses
			----------
			Input Types
			----------
		"""

		user = request.user
		group_obj = get_object_or_404(Group, key=group)
		if not have_permission_for_group(group, user):
			return Response(
				status=status.HTTP_401_UNAUTHORIZED,
				data={"detail": "you dont have permission for this group."})

		all_movies_keys = all_movies_in_group(group)
		if movie not in all_movies_keys:
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "movie not found as one of the group members movie."})

		movie = get_object_or_404(Movie, key=movie)
		group_obj.movie_of_the_week = movie
		group_obj.save()
		movie.watched = True
		movie.save()
		return Response(
			status=status.HTTP_200_OK,
			data={"detail": "'{0}' selected as movie of the week.".format(movie.name)})


class AllUserGroups(APIView):
	""" return all groups of authenticated user. """
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, format=None):
		"""
			Attributes
			----------
			Responses
			----------
			Input Types
			----------
		"""

		user = request.user
		groups = user.profile.group.all()
		serializer = GroupSerializer(instance=groups, many=True)
		return Response(status=status.HTTP_200_OK, data=serializer.data)


class AllGroupMembersProfile(APIView):
	""" return all group memebers of the group. group key should pass in url and available only for group members. """
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, group_key, format=None):
		"""
			Attributes
			----------
			Responses
			----------
			Input Types
			----------
		"""

		user = request.user
		if not have_permission_for_group(group_key, user):
			return Response(
				status=status.HTTP_401_UNAUTHORIZED,
				data={"detail": "you dont have permission for this group."})

		group = get_object_or_404(Group, key=group_key)
		all_members = Profile.objects.filter(group=group)
		group_serializer = GroupMemberSerializer(instance=all_members, many=True)
		return Response(status=status.HTTP_200_OK, data=group_serializer.data)


class GenerateInviteCode(APIView):
	""" admin only and on get should pass group key. and return invite code. """
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, group_key, format=None):
		"""
			Attributes
			----------
			Responses
			----------
			Input Types
			----------
		"""

		user = request.user
		if not is_admin_user(group_key, user):
			return Response(
				status=status.HTTP_403_FORBIDDEN,
				data={"detail": "you dont have permission to perform this action."})

		group = get_object_or_404(Group, key=group_key)
		group.invite_code = invite_code()
		group.save()
		return Response(status=status.HTTP_200_OK, data={"code": group.invite_code})


class JoinGroup(APIView):
	""" available for all authenticated users. invitation code should pass in url. """
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, invite_code, format=None):
		"""
			Attributes
			----------
			Responses
			----------
			Input Types
			----------
		"""

		user = request.user
		if not Group.objects.filter(invite_code=invite_code).exists():
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "requested group does not exist, please inform the admin to generate a new key."})

		group = get_object_or_404(Group, invite_code=invite_code)
		user.profile.group.add(group)
		return Response(
			status=status.HTTP_200_OK,
			data={"detail": "you are now a member of group '{0}'.".format(group.name)})


class LeaveGroup(APIView):
	""" available for all authenticated users. group_key should pass in url. """
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, group_key, format=None):
		"""
			Attributes
			----------
			Responses
			----------
			Input Types
			----------
		"""

		user = request.user
		group = get_object_or_404(Group, key=group_key)
		if not user.profile.group.filter(group).exists():
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={"detail": "you are not member of this group."})

		user.profile.group.remove(group)
		return Response(
			status=status.HTTP_200_OK,
			data={"detail": "you are not member of '{}' group anymore.".format(group.name)})

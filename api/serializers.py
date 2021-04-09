from rest_framework import serializers
from .models import Group, Movie
from django.contrib.auth.models import User
from customauth.models import Profile


class AdminSerializer(serializers.ModelSerializer):
	"""
		used as base of admin field in MovieSerializer and GroupSerializer serializers
		only retrive admin username.
		model = User

	"""

	class Meta:
		model = User
		fields = ("username", )


class MovieSerializer(serializers.ModelSerializer):
	"""
		used AdminSerializer serializer to get owner user username and show it in
		returning data.
		model = Movie

	"""

	user = AdminSerializer(read_only=True, many=False)

	class Meta:
		model = Movie
		fields = (
			"key", "name", "description", "user", "year", "imdb_rate", "watched",
			"download_link", "poster_link")


class MovieProfileSerializer(serializers.ModelSerializer):
	"""
		its quite similar to MovieSerializer but it dont contain user in fields.
		we use it as a related object in MemberSerializer.
		it used to show each user movie in public to group members endpoint.
		model = Movie

	"""

	class Meta:
		model = Movie
		fields = (
			"key", "name", "description", "year", "imdb_rate", "watched",
			"download_link", "poster_link", "review")


class MemberSerializer(serializers.ModelSerializer):
	"""
		used to show each user username and movies of it.
		model = User
	"""
	movies = MovieProfileSerializer(many=True, source='movie')

	class Meta:
		model = User
		fields = ("username", "movies")


class GroupSerializer(serializers.ModelSerializer):
	"""
		used to show Group information.
		used AdminSerializer to relativly get group admin user username.
		model = Group
	"""

	admin = AdminSerializer(read_only=True, many=False)

	class Meta:
		model = Group
		fields = (
			"key", "name", "movie_of_the_week", "admin", "image", "meeting_detail")


class GroupMemberSerializer(serializers.ModelSerializer):
	"""
		used to show group members key, movies, image, username.
	"""

	user = MemberSerializer(read_only=True)

	class Meta:
		model = Profile
		fields = ("key", "image", "user")

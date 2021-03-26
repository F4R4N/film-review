from rest_framework import serializers
from .models import Group, Movie
from django.contrib.auth.models import User
from customauth.models import Profile

class AdminSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ("username", )

class MovieSerializer(serializers.ModelSerializer):
	user = AdminSerializer(read_only=True, many=False)

	class Meta:
		model = Movie
		fields = ("key", "name", "description", "user", "year", "imdb_rate", "watched", "download_link", "poster_link")

class MovieProfileSerializer(serializers.ModelSerializer):

	class Meta:
		model = Movie
		fields = ("key", "name", "description", "year", "imdb_rate", "watched", "download_link", "poster_link", "review")


class MemberSerializer(serializers.ModelSerializer):
	movies = MovieProfileSerializer(many=True, source='movie')
	
	class Meta:
		model = User
		fields = ("username", "movies")


class GroupSerializer(serializers.ModelSerializer):
	admin = AdminSerializer(read_only=True, many=False)
	
	class Meta:
		model = Group
		fields = ("key", "name", "movie_of_the_week", "admin")

class GroupMemberSerializer(serializers.ModelSerializer):
	user = MemberSerializer(read_only=True)
	class Meta:
		model = Profile
		fields = ("key", "image", "user")

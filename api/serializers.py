from rest_framework import serializers
from .models import Group, Movie
from django.contrib.auth.models import User


class AdminSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ("username", )


class MovieSerializer(serializers.ModelSerializer):
	user = AdminSerializer(read_only=True, many=False)

	class Meta:
		model = Movie
		fields = ("key", "name", "description", "user", "year", "imdb_rate", "status", "download_link", "poster_link")


class GroupSerializer(serializers.ModelSerializer):
	admin = AdminSerializer(read_only=True, many=False)
	
	class Meta:
		model = Group
		fields = ("key", "name", "movie_of_the_week", "admin", "invite_link")
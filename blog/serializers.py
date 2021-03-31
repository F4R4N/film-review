from rest_framework import serializers
from .models import Post, Tag, Comment
from django.contrib.auth.models import User

class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		fields = ("name", "slug")

class AuthorSerializer(serializers.ModelSerializer):
	key = serializers.CharField(source='profile.key')
	class Meta:
		model = User
		fields = ("key", "username")

class PostSerializer(serializers.ModelSerializer):
	tags = TagSerializer(many=True)
	author = AuthorSerializer()
	class Meta:
		model = Post
		fields = ("key", "title", "body", "author", "tags", "image", "visibility", "created", "updated", "visits")

class CommentSerializer(serializers.ModelSerializer):
	post = PostSerializer()
	author = AuthorSerializer()
	class Meta:
		model = Comment
		fields = ("key", "post", "author", "body", "created")
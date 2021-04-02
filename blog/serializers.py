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

class DemoPostSerializer(serializers.ModelSerializer):
	author = AuthorSerializer()
	class Meta:
		model = Post
		fields = ("key", "title", "created", "author", )

class CommentSerializer(serializers.ModelSerializer):
	author = AuthorSerializer()
	class Meta:
		model = Comment
		fields = ("key", "author", "body", "created")

class PostSerializer(serializers.ModelSerializer):
	tags = TagSerializer(many=True)
	author = AuthorSerializer()
	comments = CommentSerializer(many=True)
	class Meta:
		model = Post
		fields = ("key", "title", "body", "author", "tags", "image", "visibility", "created", "updated", "visits", "comments")
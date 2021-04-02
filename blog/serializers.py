from rest_framework import serializers
from .models import Post, Tag, Comment
from django.contrib.auth.models import User

class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		fields = ("name", "slug")

class AuthorSerializer(serializers.ModelSerializer):
	"""
		needed data from ahtor to send in PostSerializer and CommentSerializer is only profile.key and username
	"""
	key = serializers.CharField(source='profile.key')
	class Meta:
		model = User
		fields = ("key", "username")

class DemoPostSerializer(serializers.ModelSerializer):
	"""
		to ensure visits are not fake just by loading the data in frontend. first send demodata that is small part of data .
		then user can access the full data of post with entering the given link and there we can add  visit
	"""
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
	"""
		full data of a post that if the user click on link of demodata will see.
		tags, author of post and comments are relations in database so we use their serializers to access the related data.
		'comments' are backward relational queryset . original should be comment_set but renamed to comments in models.comment
	"""
	tags = TagSerializer(many=True)
	author = AuthorSerializer()
	comments = CommentSerializer(many=True)
	class Meta:
		model = Post
		fields = ("key", "title", "body", "author", "tags", "image", "visibility", "created", "updated", "visits", "comments")
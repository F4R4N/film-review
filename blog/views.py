from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Post, Tag
from .serializers import PostSerializer

class CreateAndGetUserPost(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def post(self, request, format=None):
		user = request.user
		fields = ["title", "body", "visibility"]
		for field in fields:
			if not field in request.data:
				return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "field '{0}' is required.".format(field)})
		valid_visibilities = ["draft", "group", "all"]
		if not request.data["visibility"] in valid_visibilities:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "value '{0}' is not valid.".format(request.data["visibility"]), "valid values": valid_visibilities})
		post = Post.objects.create(
			title=request.data["title"],
			body=request.data["body"],
			visibility=request.data["visibility"],
			author=user,
		)

		if "image" in request.data:
			post.image = request.data["image"]
		if "tags" in request.data:
			for tag in request.data["tags"]:
				try:
					tag_obj = Tag.objects.get(name=tag)
				except Tag.DoesNotExist:
					tag_obj = Tag.objects.create(name=tag)
				post.tags.add(tag_obj)
		post.save()
		return Response(status=status.HTTP_201_CREATED, data={"detail": "post created."})

	def get(self, request, format=None):
		user = request.user
		posts = Post.objects.filter(author=user)
		serializer = PostSerializer(instance=posts, many=True)
		return Response(status=status.HTTP_200_OK, data=serializer.data)

class EditAndDeletePost(APIView):
	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, key, format=None):
		post = get_object_or_404(Post, key=key)
		if post.author != request.user:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "you dont have permission to perform this action."})
		if len(request.data) == 0:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "no new data provided."})
		if "title" in request.data:
			post.title = request.data["title"]
		if "body" in request.data:
			post.body = request.data["body"]
		if "visibility" in request.data:
			valid_visibilities = ["draft", "group", "all"]
			if not request.data["visibility"] in valid_visibilities:
				return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "value '{0}' is not valid.".format(request.data["visibility"]), "valid values": valid_visibilities})
			post.visibility = request.data["visibility"]
		if "image" in request.data:
			post.image = request.data["image"]
		if "tags" in request.data:
			for tag in request.data["tags"]:
				try:
					tag_obj = Tag.objects.get(name=tag)
				except Tag.DoesNotExist:
					tag_obj = Tag.objects.create(name=tag)
				post.tags.add(tag_obj)
		post.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "updated"})

	def delete(self, request, key, format=None):
		post = get_object_or_404(Post, key=key)
		if post.author != request.user:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "you dont have permission to perform this action."})
		post.delete()
		return Response(status=status.HTTP_200_OK, data={"detail": "deleted"})
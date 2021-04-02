from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Post, Tag, Comment
from api.models import Group
from .serializers import PostSerializer, DemoPostSerializer, CommentSerializer
from .utils import CustomPaginator


class CreateAndGetUserPost(APIView):
	""" 
	on GET return all post of the authenticated user. 
	on POST create new post with fields: 
		required=(title, body, visibility) 
		optional=(image, tags) 'tags' is an array of tags name if not exist create new one 

	"""
	permission_classes = (permissions.IsAuthenticated, )

	def post(self, request, format=None):
		"""
			Attributes
			----------
			user -> User(object) : authenticated user which sending the request
			required_fields -> list : list of required fields should be in request.data
			valid_visibilities -> list : list of visibilities that user can use in request.data
			post -> Post(object) : include the post object that create with user provided data
			tag_obj -> Tag(object) : contain user desired tag object

			Responses
			----------
			400 -> key="detail", value="field '{0}' is required." {0} can be : ["title", "body", "visibility"]
			400 -> [key="detail", value="value '{0}' is not valid." {0} is request.data["visibility"] provided by user], [key="valid values", value=["draft", "group", "all"]]
			201 -> key="detail", value="post created."

			Input Types
			----------

			Required:
			request.data["title"] -> String
			request.data["body"] -> String
			request.data["visibility"] -> String (of choices ["draft", "group", "all"])
			
			Optional:
			request.data["image"] -> Image
			request.data["tags"] -> Array (of tags name)
		"""
		user = request.user
		required_fields = ["title", "body", "visibility"]
		# check if all required fields are included in 'request.data'
		for field in required_fields:
			if not field in request.data:
				return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "field '{0}' is required.".format(field)})
		valid_visibilities = ["draft", "group", "all"]
		# check if user provided 'visibility' type is in valid types or not
		if not request.data["visibility"] in valid_visibilities:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "value '{0}' is not valid.".format(request.data["visibility"]), "valid values": valid_visibilities})
		# create a post object in database with the given data
		post = Post.objects.create(
			title=request.data["title"],
			body=request.data["body"],
			visibility=request.data["visibility"],
			author=user,
		)
		# 'image' and 'tags' are two optional fields. chack if provided then add them to the 'post' object
		if "image" in request.data:
			post.image = request.data["image"]
		if "tags" in request.data:
			# request.data["tags"] is a json array. iterate in the list and if exist add them to the object.
			for tag in request.data["tags"]:
				# if tags dont exist create one
				try:
					tag_obj = Tag.objects.get(name=tag)
				except Tag.DoesNotExist:
					tag_obj = Tag.objects.create(name=tag)
				# add tag to ManyToMany field with name 'tags'
				post.tags.add(tag_obj)
		# save 'image' and 'tags' if provided
		post.save()

		return Response(status=status.HTTP_201_CREATED, data={"detail": "post created."})

	def get(self, request, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			posts -> django.db.models.query.QuerySet(object) : queryset of all Post objects that author is the authenticated user
			serializer -> blog.serializers.PostSerializer(object) : contain serialized data of 'posts' queryset

			Responses
			----------
			200 -> return seialized data in serializer variable, return all posts that author of it is user that sending the request

		"""
		user = request.user
		# get all posts that author is 'user'
		posts = Post.objects.filter(author=user)
		# serialize the object with 'many=True' allow us to serialize a queryset of post
		serializer = PostSerializer(instance=posts, many=True)
		return Response(status=status.HTTP_200_OK, data=serializer.data)

class EditAndDeletePost(APIView):
	""" 
		should pass post key in url.
		mothods=[
			PUT=('title', 'body', 'visibility', 'image', 'tags') visibility should be choice of ('draft', 'group', 'all')
			DELETE=just pass the post key in url path
		]
	"""
	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, post_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			post -> blog.models.Post(object) : contain post object that 'key'= provided key in the url if not exist return 404
			
			Responses
			----------
			404 -> key="detail", value="Not found." : if the given 'key' in the url is not refer to a Post object
			403 -> key="detail", value="you dont have permission to perform this action." : if user sending the request not post author
			400 -> key="detail", value="no new data provided." : if not key exist in request.data
			400 -> [key="detail", value="value '{0}' is not valid." {0} is request.data["visibility"] provided by user], [key="valid values", value=["draft", "group", "all"]]
			200 -> key="detail", value="updated"

			Input Types
			----------
			Required
			no required field. but at least one field should be in request.
			post_key -> String : in the url

			Optional
			request.data["title"] -> String
			request.data["body"] -> String
			request.data["visibility"] -> String (of choices ["draft", "group", "all"])
			request.data["image"] -> Image
			request.data["tags"] -> Array (of tags name)

		"""
		user = request.user

		# get the post that editing should perform on it
		post = get_object_or_404(Post, key=post_key)

		# check if user own the post or not if not return unathorized
		if post.author != user:
			return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission to perform this action."})
		# check if reques.data is not empty
		if len(request.data) == 0:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "no new data provided."})

		# all the fields sending are optional so we check for every of them are included or not
		if "title" in request.data:
			post.title = request.data["title"]
		if "body" in request.data:
			post.body = request.data["body"]
		if "visibility" in request.data:
			valid_visibilities = ["draft", "group", "all"]

			# check if given vissibility is valid and in choices
			if not request.data["visibility"] in valid_visibilities:
				return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "value '{0}' is not valid.".format(request.data["visibility"]), "valid values": valid_visibilities})
			post.visibility = request.data["visibility"]
		if "image" in request.data:
			post.image = request.data["image"]

		# request.data["tags"] is a json array. iterate in the list and if exist add them to the object.
		if "tags" in request.data:
			for tag in request.data["tags"]:
				try:
					tag_obj = Tag.objects.get(name=tag)
				except Tag.DoesNotExist:
					tag_obj = Tag.objects.create(name=tag)
				post.tags.add(tag_obj)

		# save fields that modified
		post.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "updated"})

	def delete(self, request, post_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			post -> blog.models.Post(object) : contain post object that 'key'= provided key in the url if not exist return 404

			Responses
			----------
			404 -> key="detail", value="Not found." : if the given 'key' in the url is not refer to a Post object
			403 -> key="detail", value="you dont have permission to perform this action." : if user sending the request not post author
			200 -> key="detail", value="deleted"

			Input Types
			----------
			post_key -> String : in the url
			
		"""
		user = request.user
		post = get_object_or_404(Post, key=post_key)
		if post.author != user:
			return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission to perform this action."})
		post.delete()
		return Response(status=status.HTTP_200_OK, data={"detail": "deleted"})


class AllPublicPostsPaginated(generics.ListAPIView):
	"""
		return all posts with 'visibility="all"' 
		to prevent load all data at once add paginatior . 
		with scroll should get next page for that pass parameter 'page' to url like '.../?page=2'.
	"""
	permission_classes = (permissions.IsAuthenticated, )
	queryset = Post.objects.filter(visibility="all")
	serializer_class = DemoPostSerializer
	# paginator class is defined in .utils.py . 'page_size' = 5 and page parameter to access difrent pages is 'page'
	pagination_class = CustomPaginator


class DesiredPost(APIView):
	"""
		return all data of the desierd post. post key should pass in url.
	"""
	permission_classes = (permissions.IsAuthenticated, )

	def get(self, request, post_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			post -> blog.models.Post(object) : contain post object that 'post_key' provided key in the url if not exist return 404
			serializer -> blog.serializers.PostSerializer(object) : contain serialized data of 'post' object
			
			Responses
			----------
			404 -> key="detail", value="Not found." : if the post with the given post_key not found
			403 -> key="detail", value="this post is restricted to group and you are not part of the group." : if user is not member of any groups that author of post is a member of
			200 -> return serialized data of the post you passed 'post_key' in url

			Input Types
			----------
			post_key -> String : in the url
		"""
		user = request.user
		post = get_object_or_404(Post, key=post_key)
		# check if the desiered post restricted to the group members
		if post.visibility == "group":
			# all geoups that author of the post is member of them
			author_groups = post.author.profile.group.all()
			# store if user is in the authors group or not
			is_member = []
			for igroup in author_groups:
				# check if any of user group key is equal to igroup.key. if it was append "True" to "is_member" else append "False"
				if user.profile.group.filter(key=igroup.key).exists():
					is_member.append(True)
				else:
					is_member.append(False)
			# if not user is member of at least one of author group return forbiden response
			if not any(is_member):
				return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "this post is restricted to group and you are not part of the group."})
		# else return the proper serialized json object
		serializer = PostSerializer(instance=post)
		# and also add 1 to visits
		post.visits += 1
		post.save()
		return Response(status=status.HTTP_200_OK, data=serializer.data)

class GroupPublicPostsPaginated(APIView):
	"""
		return all posts with 'visibility="group"'
		in the given group key . group_key should pass in url		
	"""
	permission_classes = (permissions.IsAuthenticated, )
	
	def get(self, request, group_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			group -> api.models.Group(object) : the group object that group_key sent as parameter
			posts -> django.db.models.query.QuerySet(object) : contain all posts with 'visibility="group"' and where author is part of the group
			serializer -> blog.serializers.DemoPostSerializer(object) : contain serialized object with "many='True'"

			Responses
			----------
			400 -> key="detail", value="you are not member of this group." : if user is not member of the group that group_key passed in the url
			404 -> key="detail", value="Not found." : if the group with the given group_key not found
			200 -> return serialized data

			Input Types
			----------
			group_key -> String : in the url
		"""
		user = request.user
		# check if user is member of group
		if not user.profile.group.filter(key=group_key).exists():
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "you are not member of this group."})
		group = get_object_or_404(Group, key=group_key)
		# queryset of posts that theyre author is part of the given group and visibility is "group" restricted
		posts = Post.objects.filter(author__profile__group=group, visibility="group")
		serializer = DemoPostSerializer(instance=posts, many=True)
		return Response(status=status.HTTP_200_OK, data=serializer.data)


class CreateComment(APIView):
	"""
		is available for authenticated users.
		field 'body' is required. and post_key should include in url.
	"""
	permission_classes = (permissions.IsAuthenticated, )

	def post(self, request, post_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			comment -> blog.models.Comment(object) : comment object that create by user data

			Responses
			----------
			400 -> key="detail", value="field 'body' is required." : if 'body' key not in request.data
			404 -> key="detail", value="Not found." : if the post with the given post_key not found
			201 -> [key="detail", value="comment created."], [key="data", value=(comment object)]

			Input Types
			----------
			request.data["body"] -> String
			post_key -> String : in the url
		"""
		user = request.user
		# return 400 response if "body field is not in request.data"
		if not "body" in request.data:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "field 'body' is required."})
			# create comment with with given "body" and logged in user and 'post_key' that will be send in url
		comment = Comment.objects.create(
			post=get_object_or_404(Post, key=post_key),
			author=user,
			body=request.data["body"],
		)
		return Response(status=status.HTTP_201_CREATED, data={"detail": "comment created.", "data": CommentSerializer(instance=comment).data}) # also decided to send data of comment in response


class EditAndDeleteComment(APIView):
	"""
		methods = [
			PUT= can edit comment body. is available only for comment owner. should include comment key in the url.
			DELETE= only comment owner and post owner can delete comments. should include comment key in the url.
		]
	"""
	permission_classes = (permissions.IsAuthenticated, )

	def put(self, request, comment_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			comment -> blog.models.Comment(object) : get the desired Comment object with the comment_key

			Responses
			----------
			404 -> key="detail", value="Not found." : if the given 'comment_key' in the url is not refer to a Comment object
			403 -> key="detail", value="you dont have permission to perform this action." : if user sending the request is not comment author or post owner
			400 -> key="detail", value="no new data provided." : if no field provided in request
			200 -> key="detail", value="comment modified."
			
			Input Types
			----------
			comment_key -> String : in the end of url with slash(/)
			reuqest.data["body"] -> String
		"""
		user = request.user
		comment = get_object_or_404(Comment, key=comment_key)
		# only user can edit its own comment
		if comment.author != user:
			return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission to perform this action."})
		# check if request.data not empty
		if len(request.data) == 0:
			return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "no new data provided."})
		if "body" in request.data:
			comment.body = request.data["body"]
		comment.save()
		return Response(status=status.HTTP_200_OK, data={"detail": "comment modified."})

	def delete(self, request, comment_key, format=None):
		"""
			Attributes
			----------
			user -> django.contrib.auth.models.User(object) : authenticated user which sending the request
			comment -> blog.models.Comment(object) : get the desired Comment object with the comment_key
			post_owner -> django.contrib.auth.models.User(object) : contain user object that own the post

			Responses
			----------
			404 -> key="detail", value="Not found." : if the given 'comment_key' in the url is not refer to a Comment object
			403 -> key="detail", value="you dont have permission to perform this action." : if user sending the request not comment author or post owner
			200 -> key="detail", value="deleted"

			Input Types
			----------
			comment_key -> String : in the end of url with slash(/)
		"""
		user = request.user
		comment = get_object_or_404(Comment, key=comment_key)
		post_owner = comment.post.author
		# only comment owner and post owner can delete a comment 
		if comment.author != user:
			if user != post_owner:
				return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": "you dont have permission to perform this action."})
		comment.delete()
		return Response(status=status.HTTP_200_OK, data={"detail": "deleted"})


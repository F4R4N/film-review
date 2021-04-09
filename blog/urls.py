from django.urls import path
from .views import (
	CreateAndGetUserPost, EditAndDeletePost, AllPublicPostsPaginated, DesiredPost,
	GroupPublicPostsPaginated, CreateComment, EditAndDeleteComment)

app_name = "blog"

urlpatterns = [
	path("post/", CreateAndGetUserPost.as_view()),
	path("post/<str:post_key>/", EditAndDeletePost.as_view()),
	path("posts/all/", AllPublicPostsPaginated.as_view()),
	path("posts/<str:post_key>/", DesiredPost.as_view()),
	path("posts/group/<str:group_key>/", GroupPublicPostsPaginated.as_view()),
	path("comment/create/<str:post_key>/", CreateComment.as_view()),
	path("comment/<str:comment_key>/", EditAndDeleteComment.as_view()),

]

from django.urls import path
from .views import CreateAndGetUserPost, EditAndDeletePost, AllPublicPostsPaginated, DesiredPost, GroupPublicPostsPaginated
app_name = "blog"

urlpatterns = [
	path("post/", CreateAndGetUserPost.as_view()),
	path("post/<str:key>/", EditAndDeletePost.as_view()),
	path("posts/all/", AllPublicPostsPaginated.as_view()),
	path("posts/<str:key>/", DesiredPost.as_view()),
	path("posts/group/<str:group_key>/", GroupPublicPostsPaginated.as_view()),


]
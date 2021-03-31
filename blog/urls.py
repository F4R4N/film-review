from django.urls import path
from .views import CreateAndGetUserPost, EditAndDeletePost
app_name = "blog"

urlpatterns = [
	path("post/", CreateAndGetUserPost.as_view()),
	path("post/<str:key>/", EditAndDeletePost.as_view()),

]
from .views import CreateGroupView, CreateMovieView, EditMovieView, GetRandomMovieView, SubmitMovieView, AllUserGroups, AllGroupMembersProfile
from django.urls import path

app_name = "api"
urlpatterns = [
	path("group/add/", CreateGroupView.as_view()),
	path("movie/add/", CreateMovieView.as_view()),
	path("movie/edit/<str:key>/", EditMovieView.as_view()),
	path("movie/group/select/<str:key>/", GetRandomMovieView.as_view()),
	path("movie/group/submit/<str:group>/<str:movie>/", SubmitMovieView.as_view()),
	path("group/get/", AllUserGroups.as_view()),
	path("group/all_profiles/<str:group_key>/", AllGroupMembersProfile.as_view()),
]

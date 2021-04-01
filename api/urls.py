from .views import (CreateGroupView, EditAndDeleteGroupView, EditAndDeleteMovieView, 
					CreateAndGetMovieView, GetRandomMovieView, SubmitMovieView, 
					AllUserGroups, AllGroupMembersProfile, GenerateInviteCode, JoinGroup, LeaveGroup)
from django.urls import path

app_name = "api"
urlpatterns = [
	path("group/add/", CreateGroupView.as_view()),
	path("group/<str:group_key>/", EditAndDeleteGroupView.as_view()),
	path("admin/group/invite_code/<str:group_key>/", GenerateInviteCode.as_view()),
	path("group/join/<str:invite_code>/", JoinGroup.as_view()),
	path("group/leave/<str:group_key>/", LeaveGroup.as_view()),
	path("group/movie/select/<str:key>/", GetRandomMovieView.as_view()),
	path("group/movie/submit/<str:group>/<str:movie>/", SubmitMovieView.as_view()),
	path("group/all_profiles/<str:group_key>/", AllGroupMembersProfile.as_view()),
	path("user/groups/", AllUserGroups.as_view()),
	path("movie/", CreateAndGetMovieView.as_view()),
	path("movie/<str:key>/", EditAndDeleteMovieView.as_view()),
]

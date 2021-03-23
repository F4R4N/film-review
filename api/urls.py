from .views import CreateGroup
from django.urls import path

app_name = "api"
urlpatterns = [
	path("group/add/", CreateGroup.as_view()),
]

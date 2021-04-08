from django.contrib import admin
from .models import Group, Movie


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
	list_display = (
		"name", "key", "meeting_detail", "movie_of_the_week", "admin", "invite_code")

	list_editable = ("name", "meeting_detail")
	search_fields = ("name", "meeting_detail")


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
	list_display = (
		"name", "key", "description", "review", "user", "year", "imdb_rate",
		"watched", "download_link", "poster_link")

	list_editable = (
		"name", "description", "review", "year", "imdb_rate", "watched")
	search_fields = ("name", "description", "review")

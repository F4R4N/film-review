from django.shortcuts import get_object_or_404
from .models import Group
from itertools import chain


def all_movies_in_group(key):
	group = get_object_or_404(Group, key=key)
	all_profiles = group.profile_set.all()
	all_group_movies = []
	for profile in all_profiles:
		user_movies = profile.user.movie.filter(watched=False).values_list("key", flat=True)
		all_group_movies.append(list(user_movies))
	all_group_movie_keys = list(chain.from_iterable(all_group_movies))
	return all_group_movie_keys


def have_permission_for_group(group_key, user):
	if not user.profile.group.filter(key=group_key).exists():
		return False
	return True


def is_admin_user(group_key, user):
	group = get_object_or_404(Group, key=group_key)
	if group.admin != user:
		return False
	return True

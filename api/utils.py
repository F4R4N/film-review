import random, string
from datetime import datetime

def profile_image(instance, filename):
    saved_file_name = instance.user.username + "-" + datetime.now().strftime("%Y_%m_%d,%H:%M:%S") + ".jpg"
    return 'profile/{0}/{1}'.format(instance.user.username, saved_file_name)

def group_image(instance, filename):
    saved_file_name = instance.name + "-" + datetime.now().strftime("%Y_%m_%d,%H:%M:%S") + ".jpg"
    return 'group/{0}/{1}'.format(instance.name, saved_file_name)

def random_key():
	allowed_chars = list(string.ascii_lowercase) + list(string.digits)
	random_key = ""
	key = random_key.join(random.sample(allowed_chars, 15))
	return key

def invite_code():
	allowed_chars = list(string.ascii_lowercase)
	random_key = ""
	key = random_key.join(random.sample(allowed_chars, 15))
	return "FILMMEETING" + key


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


import random
import string
from datetime import datetime


def profile_image(instance, filename):
	username = instance.user.username
	date_time = datetime.now().strftime("%Y_%m_%d,%H:%M:%S")
	saved_file_name = username + "-" + date_time + ".jpg"
	return 'profile/{0}/{1}'.format(instance.user.username, saved_file_name)


def group_image(instance, filename):
	date_time = datetime.now().strftime("%Y_%m_%d,%H:%M:%S")
	saved_file_name = instance.name + "-" + date_time + ".jpg"
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

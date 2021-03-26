import random, string
from datetime import datetime

def profile_image(instance, filename):
    saved_file_name = instance.user.username + "-" + datetime.now().strftime("%Y_%m_%d,%H:%M:%S") + ".jpg"
    return 'profile/{0}/{1}'.format(instance.user.username, saved_file_name)

def random_key():
	allowed_chars = list(string.ascii_lowercase) + list(string.digits)
	random_key = ""
	key = random_key.join(random.sample(allowed_chars, 15))
	return key

def invite_code():
	allowed_chars = list(string.ascii_lowercase)
	random_key = ""
	key = random_key.join(random.sample(allowed_chars, 15))
	return key
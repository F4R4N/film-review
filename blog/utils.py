import datetime

def post_images(instance, filename):
	date_and_time = datetime.datetime.now().strftime("%y-%m-%d.%H-%M-%S")
	path = "profile/{0}/post/{1}.jpg".format(instance.author.username, date_and_time)
	return path
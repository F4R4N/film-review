import datetime
from rest_framework import pagination


def post_images(instance, filename):
	"""
		specify proper path to store posts images in the following format
		profile/{post_author_username}/post/{date_and_time in following format
		(%y-%m-%d.%H-%M-%S)}

	"""

	date_and_time = datetime.datetime.now().strftime("%y-%m-%d.%H-%M-%S")
	username = instance.author.username
	path = "profile/{0}/post/{1}.jpg".format(username, date_and_time)
	return path


class CustomPaginator(pagination.PageNumberPagination):
	"""
		paginator object used for posts/all/ endpoint so that all of the data wont
		load at once and load them page by page. page_size is 30 now and can access
		next page by passing page parameter in the url like : posts/all/?page=2

	"""

	max_page_size = 100
	page_size = 30
	page_query_param = "page"

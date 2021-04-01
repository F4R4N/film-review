import datetime
from rest_framework import pagination

def post_images(instance, filename):
	date_and_time = datetime.datetime.now().strftime("%y-%m-%d.%H-%M-%S")
	path = "profile/{0}/post/{1}.jpg".format(instance.author.username, date_and_time)
	return path

class CustomPaginator(pagination.PageNumberPagination):
	page_size_query_param = "size"
	max_page_size = 100
	page_size = 5
	page_query_param = "page"
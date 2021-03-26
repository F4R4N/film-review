from django.db import models
from .utils import random_key, invite_code, group_image
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Movie(models.Model):
	key = models.CharField(max_length=15, default=random_key, unique=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True, blank=True)
	review = models.TextField(null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movie")
	year = models.PositiveIntegerField(validators=[MinValueValidator(1800), MaxValueValidator(datetime.datetime.now().year)], null=True, blank=True)
	imdb_rate = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)], null=True, blank=True)
	watched = models.BooleanField(default=False)
	download_link = models.URLField(null=True, blank=True)
	poster_link = models.URLField(null=True, blank=True)
	date_and_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class Group(models.Model):
	key = models.CharField(max_length=15, default=random_key)
	name = models.CharField(max_length=50)
	image = models.ImageField(upload_to=group_image, default=None)
	movie_of_the_week = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
	admin = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	invite_code = models.CharField(max_length=17, default=invite_code)
	date_and_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

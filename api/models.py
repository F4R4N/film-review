from django.db import models
from .utils import random_key, invite_url
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Movie(models.Model):
	key = models.CharField(max_length=15, default=random_key, unique=True)
	name = models.CharField(max_length=100)
	description = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	year = models.PositiveIntegerField(validators=[MinValueValidator(1800), MaxValueValidator(datetime.datetime.now().year)])
	imdb_rate = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10)])
	status = models.BooleanField()
	download_link = models.URLField()
	poster_link = models.URLField()

	def __str__(self):
		return self.name


class Group(models.Model):
	key = models.CharField(max_length=15, default=random_key)
	name = models.CharField(max_length=50)
	movie_of_the_week = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
	admin = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	invite_link = models.CharField(max_length=15, default=invite_url)

	def __str__(self):
		return self.name


class OMDBMovie(models.Model):
	json_data = models.JSONField()

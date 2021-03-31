from django.db import models
from api.utils import random_key
from django.contrib.auth.models import User
from .utils import post_images
from django.utils.text import slugify

class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(unique=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Tag, self).save(*args, **kwargs)

class Post(models.Model):
	VISIBILITY_CHOICES = (
		('draft', 'Draft'),
		('group', 'Group'),
		('all', 'All'),
	)
	key = models.CharField(default=random_key, max_length=13, unique=True)
	title = models.CharField(max_length=200)
	body = models.TextField()
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	tags = models.ManyToManyField(Tag, blank=True)
	image = models.ImageField(upload_to=post_images, blank=True)
	visibility = models.CharField(max_length=6, choices=VISIBILITY_CHOICES, default='draft')
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	visits = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.title

class Comment(models.Model):
	key = models.CharField(default=random_key, max_length=13, unique=True)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	body = models.TextField()
	is_active = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.post.title

		
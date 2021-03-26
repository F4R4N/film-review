from django.db import models
from django.contrib.auth.models import User
from api.models import Group
from api.utils import profile_image, random_key

class Profile(models.Model):
	key = models.CharField(max_length=16, default=random_key, unique=True, blank=False, null=False)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	image = models.ImageField(upload_to=profile_image, default="profile/default/default.png")
	group = models.ManyToManyField(Group)

	def __str__(self):
		return self.user.username
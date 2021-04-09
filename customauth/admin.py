from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "image", "key", )


# changed list_display and list_editable but keep default settings by inheriting UserAdmin
class MyUserAdmin(UserAdmin):
	list_display = (
		"username", "first_name", "last_name", "email", "is_active", "is_staff")

	list_editable = ("email", "is_active",)


# to save changes should unregister and re-register the model in Admin Panel
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

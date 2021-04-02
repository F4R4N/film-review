from django.contrib import admin
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# admin.site.register(Profile)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "image", "key", )

class MyUserAdmin(UserAdmin):
	list_display = ("username", "first_name", "last_name", "email", "is_active", "is_staff", )
	list_editable = ("email", "is_active",)

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
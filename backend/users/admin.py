from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Company

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Company)
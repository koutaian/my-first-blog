from django.contrib import admin
from .models import User, Class


class UserAdmin(admin.ModelAdmin):
    fields = ("username","password",)

admin.site.register(User, UserAdmin)
admin.site.register(Class)

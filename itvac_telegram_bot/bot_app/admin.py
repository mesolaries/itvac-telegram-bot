from django.contrib import admin
from .models import User, Alert

# Register your models here.

admin.site.register(User)
admin.site.register(Alert)
from django.db import models

# Create your models here.

# All users


class User(models.Model):
    username = models.CharField(max_length=64, blank=True)
    chat_id = models.IntegerField(unique=True)

    def __str__(self):
        return self.username

# Users who activated reminder


class Reminder(models.Model):
    chat_id = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.chat_id)

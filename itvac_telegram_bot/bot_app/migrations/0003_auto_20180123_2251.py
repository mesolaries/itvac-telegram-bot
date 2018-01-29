# Generated by Django 2.0.1 on 2018-01-23 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_app', '0002_auto_20180123_2133'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reminder',
            name='user_id',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_id',
        ),
        migrations.AddField(
            model_name='reminder',
            name='chat_id',
            field=models.IntegerField(default=0, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='chat_id',
            field=models.IntegerField(default=0, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]

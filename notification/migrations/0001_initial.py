# Generated by Django 3.2.7 on 2021-10-26 13:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=256, null=True)),
                ('message', models.TextField()),
                ('read', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('post_like', 'post like'), ('post_comment', 'post comment'), ('chat_message', 'chat message')], max_length=20)),
                ('object_id', models.CharField(max_length=50)),
                ('image_url', models.URLField(blank=True)),
                ('post_image', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_device_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FCMDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device', models.TextField()),
                ('participant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='device', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
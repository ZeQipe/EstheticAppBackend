# Generated by Django 5.1 on 2024-09-08 05:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('post_name', models.CharField(max_length=20)),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
                ('type_content', models.TextField()),
                ('url', models.TextField(unique=True)),
                ('tags_list', models.JSONField(default=list)),
                ('aspect_ratio', models.TextField(blank=True, null=True)),
                ('object_position', models.TextField(blank=True, null=True)),
                ('link', models.CharField(max_length=100)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='users.user')),
                ('users_liked', models.ManyToManyField(blank=True, related_name='liked_posts', to='users.user')),
            ],
        ),
    ]

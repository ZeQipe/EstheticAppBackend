# Generated by Django 5.1 on 2024-09-08 05:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('posts', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=200)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='users.user')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.post')),
                ('users_liked', models.ManyToManyField(blank=True, related_name='liked_comments', to='users.user')),
            ],
        ),
    ]

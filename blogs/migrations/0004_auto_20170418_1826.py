# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-18 18:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0003_auto_20170415_0502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='blog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post', to='blogs.Blog'),
        ),
        migrations.AlterField(
            model_name='post',
            name='picture',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='post',
            name='posted_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 3.2b1 on 2021-03-18 08:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Capital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yyyy', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1989), django.core.validators.MaxValueValidator(2099)], verbose_name='年')),
                ('m1', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000)], verbose_name='現金')),
                ('m2', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000)], verbose_name='その他の預金')),
                ('m3', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000)], verbose_name='前払金')),
                ('m4', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000000)], verbose_name='未払金')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '元入金',
                'db_table': 'fsjs_capitals',
            },
        ),
    ]
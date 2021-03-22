# Generated by Django 3.2b1 on 2021-03-17 05:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=20, unique=True, validators=[django.core.validators.MaxLengthValidator(20)], verbose_name='名前')),
                ('types', models.IntegerField(db_index=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)], verbose_name='種類')),
                ('expense_flg', models.BooleanField(db_index=True, default=False, verbose_name='経費フラグ')),
                ('sort_list', models.IntegerField(validators=[django.core.validators.MaxValueValidator(1000)], verbose_name='表示順序(リスト用)')),
                ('sort_expense', models.IntegerField(validators=[django.core.validators.MaxValueValidator(1000)], verbose_name='表示順序(経費用)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '勘定科目',
                'db_table': 'fsjs_accounts',
            },
        ),
    ]
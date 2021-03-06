# Generated by Django 2.2.7 on 2019-11-19 11:40

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
            name='Category',
            fields=[
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(primary_key=True, serialize=False, unique=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Draft'), (1, 'Published')], default=0)),
                ('title', models.CharField(max_length=254)),
                ('directions', models.TextField(blank=True)),
                ('ingredients', models.TextField(blank=True)),
                ('edit_date', models.DateTimeField(auto_now_add=True)),
                ('pub_date', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(related_name='recipes', to='catalog.Category')),
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
                'ordering': ['-pub_date', '-edit_date'],
            },
        ),
    ]

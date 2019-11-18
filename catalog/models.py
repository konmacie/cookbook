from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

import json


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    name = models.CharField(
        blank=False,
        unique=True,
        max_length=50,
    )

    def __str__(self):
        return str(self.name)


class Recipe(models.Model):
    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-pub_date', '-edit_date']

    # choices for Recipe.status field
    STATUS_DRAFT, STATUS_PUBLISHED = range(2)
    _STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    )

    # fields
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='recipes',
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField(
        Category,
        related_name='recipes',
    )
    status = models.PositiveSmallIntegerField(
        choices=_STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    title = models.CharField(max_length=254, blank=False)
    directions = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    edit_date = models.DateTimeField(auto_now_add=True)
    pub_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.pk})

    @property
    def ingredients_list(self):
        '''
        Return ingredients as list of dicts, as such can be used
        as formset initial.
        [{'desc':...}, {'desc':...}, ]
        '''
        if not self.ingredients:
            return []
        return json.loads(self.ingredients)

    @property
    def directions_list(self):
        '''
        Returns directions as list of dicts, as such can be used
        as formset initial.
        [{'desc':...}, {'desc':...}, ]
        '''
        if not self.directions:
            return []
        return json.loads(self.directions)

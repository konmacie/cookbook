""" Views available without authentication """

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.db.models import Count

import json
from datetime import datetime

from catalog.forms import (
    RecipeForm, IngredientFormSet, DirectionFormSet, RecipePhotoForm)
from catalog.models import Recipe, Category, Favourite


class IndexView(TemplateView):
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        latest_recipes = Recipe.objects\
            .filter(status=Recipe.STATUS_PUBLISHED)\
            .select_related('author')[:10]

        popular_recipes = Recipe.objects\
            .filter(status=Recipe.STATUS_PUBLISHED)\
            .annotate(like_count=Count('favourite'))\
            .filter(like_count__gte=1)\
            .order_by('-like_count', '-pub_date')[:10]
        context['latest_recipes'] = latest_recipes
        context['popular_recipes'] = popular_recipes
        return context


class RecipeDetail(DetailView):
    """
    Shows details of selected recipe with status 'published'.
    """
    model = Recipe
    context_object_name = 'recipe'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset\
            .filter(status=Recipe.STATUS_PUBLISHED)\
            .prefetch_related('categories')\
            .annotate(like_count=Count('favourite'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if user authenticated, check if they liked the recipe
        is_liked = False
        if self.request.user.is_authenticated:
            is_liked = Favourite.objects.filter(
                recipe=self.object,
                user=self.request.user
            ).exists()
        context['is_liked'] = is_liked
        return context


class RecipesByCategoryList(ListView):
    """
    Shows list of published recipes in selected category.
    """
    model = Recipe
    context_object_name = 'recipes_list'
    template_name = 'catalog/recipes_list.html'
    paginate_by = 10
    allow_empty = True

    def get_queryset(self):
        # get Category's slug from url
        slug = self.kwargs.get('slug')
        self.category = get_object_or_404(Category, slug=slug)
        # get queryset of recipes from that category
        queryset = self.category.recipes\
            .filter(status=Recipe.STATUS_PUBLISHED)\
            .select_related('author')
        return queryset

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data()
        context.update(category=self.category)
        context.update(title=str(self.category))
        return context


class RecipesNewest(ListView):
    """
    Shows up to 100 most recent recipes with status 'published'.
    """
    model = Recipe
    context_object_name = 'recipes_list'
    template_name = 'catalog/recipes_list.html'
    paginate_by = 10
    allow_empty = True

    extra_context = {
        'title': 'Newest recipes'
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=Recipe.STATUS_PUBLISHED)[:100]
        return queryset


class RecipesPopular(ListView):
    """
    Shows up to 100 most liked recipes with status 'published'.
    """
    model = Recipe
    context_object_name = 'recipes_list'
    template_name = 'catalog/recipes_list.html'
    paginate_by = 10
    allow_empty = True

    extra_context = {
        'title': 'Most liked recipes'
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(status=Recipe.STATUS_PUBLISHED)\
            .annotate(like_count=Count('favourite'))\
            .filter(like_count__gte=1)\
            .order_by('-like_count', '-pub_date')[:100]
        return queryset

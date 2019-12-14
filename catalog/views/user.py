""" Views needing user to be authenticated """

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.urls import reverse

import json
from datetime import datetime

from catalog.forms import (
    RecipeForm, IngredientFormSet, DirectionFormSet, RecipePhotoForm)
from catalog.models import Recipe, Category, Favourite


@login_required
@transaction.atomic  # atomic in case save_m2m() failed
def recipe_create_draft(request):
    """
    View for creating new recipe with status 'draft'.
    Has only 2 fields in the form: title and categories.
    Ingerdients and directions can be set in edit view.
    After succesfully commiting new draft, redirects to edit view.
    """
    if request.method == "POST":
        recipe_form = RecipeForm(request.POST, prefix='recipe')

        if recipe_form.is_valid():
            # Create Recipe object. commit = False since we need to manually
            # set Author field before saving to db.
            recipe = recipe_form.save(commit=False)
            recipe.author = request.user

            # Save recipe do db.
            recipe.save()

            # Since earlier was used commit=False, we need to save m2m
            # relations manually.
            recipe_form.save_m2m()

            # add success message
            messages.add_message(
                request, messages.SUCCESS,
                "Draft created succesfully!",
                extra_tags="alert-success"
            )
            messages.add_message(
                request, messages.INFO,
                "You can now edit new recipe's draft. Be aware, that after "
                "publishing, recipe can't be edited.",
                extra_tags="alert-info"
            )
            return redirect(reverse('recipe_edit', kwargs={'pk': recipe.pk}))
    else:
        recipe_form = RecipeForm(prefix='recipe')

    context = {
        'recipe_form': recipe_form,
    }
    return render(request, 'catalog/recipe_create.html', context)


@login_required
@transaction.atomic  # atomic in case save_m2m() failed
def recipe_edit(request, pk):
    """
    View used to edit and publish existing Recipe object.
    Recipe must have status 'draft' and user must be an author to have access.
    """
    recipe = get_object_or_404(Recipe, pk=pk, status=Recipe.STATUS_DRAFT)
    # check if user is recipe's author
    if recipe.author != request.user:
        raise PermissionDenied()

    if request.method == "POST":
        recipe_form = RecipeForm(
            instance=recipe, data=request.POST, prefix='recipe')
        photo_form = RecipePhotoForm(
            request.POST, request.FILES, prefix='photo')
        ingredient_formset = IngredientFormSet(
            request.POST, prefix='ingredients',
            initial=recipe.ingredients_list)
        direction_formset = DirectionFormSet(
            request.POST, prefix='directions',
            initial=recipe.directions_list)

        if (recipe_form.is_valid()
                and ingredient_formset.is_valid()
                and direction_formset.is_valid()
                and photo_form.is_valid()):
            # Dumping ingredient_formset into json string.
            ingredients_list = [{'desc': form.cleaned_data.get('desc')}
                                for form in ingredient_formset
                                if form.cleaned_data.get('desc')]
            ingredients = json.dumps(ingredients_list)

            # Dumping direction_formset into json string.
            directions_list = [{'desc': form.cleaned_data.get('desc')}
                               for form in direction_formset
                               if form.cleaned_data.get('desc')]
            directions = json.dumps(directions_list)

            # add warning message if ing. or dir. list is empty
            if not ingredients_list or not directions_list:
                messages.add_message(
                    request, messages.WARNING,
                    "Ingredients list or directions list is empty, "
                    "this recipe can't be published.",
                    extra_tags="alert-warning"
                )

            # get photo file if uploaded
            photo = request.FILES.get('photo-photo', None)

            # Set ingredients and directions to respective Recipe fields
            # and save object.
            recipe_form.save(commit=False)
            if photo:
                recipe.photo = photo
            recipe.ingredients = ingredients
            recipe.directions = directions
            recipe.save()
            recipe_form.save_m2m()

            # add success message
            messages.add_message(
                request, messages.SUCCESS,
                "Draft saved succesfully!",
                extra_tags="alert-success"
            )

            # Check which button was clicked
            if request.POST.get('save_publish'):
                # If 'Save and publish'
                return redirect(
                    reverse('recipe_publish', kwargs={'pk': recipe.pk}))
            # If 'Save draft' stays on the same page
            else:

                return redirect(recipe)

    else:
        recipe_form = RecipeForm(instance=recipe, prefix='recipe')
        photo_form = RecipePhotoForm(prefix='photo')
        ingredient_formset = IngredientFormSet(
            prefix='ingredients', initial=recipe.ingredients_list)
        direction_formset = DirectionFormSet(
            prefix='directions', initial=recipe.directions_list)

    context = {
        'recipe': recipe,
        'recipe_form': recipe_form,
        'photo_form': photo_form,
        'ingredients_formset': ingredient_formset,
        'directions_formset': direction_formset,
    }
    return render(request, 'catalog/recipe_edit.html', context)


@login_required
def recipe_publish(request, pk):
    """
    For confirming publication of a recipe.
    With GET method shows template and confirmation form.
    With POST method publishes recipe and redirects to recipe's detail view.
    """
    recipe = get_object_or_404(Recipe, pk=pk, status=Recipe.STATUS_DRAFT)
    if recipe.author != request.user:
        raise PermissionDenied()

    if not recipe.ingredients_list or not recipe.directions_list:
        # add error message
        messages.add_message(
            request, messages.ERROR,
            "Can't publish recipe - ingredients list and "
            "directions list can't be empty.",
            extra_tags="alert-danger"
        )
        return redirect(reverse('recipe_edit', kwargs={'pk': recipe.pk}))

    if request.method == 'POST':
        recipe.status = Recipe.STATUS_PUBLISHED
        recipe.pub_date = datetime.now()
        recipe.save()

        # add success message
        messages.add_message(
            request, messages.SUCCESS,
            "Recipe published succesfully!",
            extra_tags="alert-success"
        )
        return redirect(recipe)

    # If 'GET' method
    context = {
        'recipe': recipe,
    }
    return render(request, 'catalog/recipe_publish.html', context)


@login_required
def recipe_delete(request, pk):
    """
    For confirming deletion of a recipe.
    With GET method shows template and confirmation form.
    With POST method deletes recipe and redirects to index.
    Recipe must have status 'draft'.
    """
    recipe = get_object_or_404(Recipe, pk=pk, status=Recipe.STATUS_DRAFT)
    if recipe.author != request.user:
        raise PermissionDenied()

    if request.method == 'POST':
        recipe.delete()
        # add success message
        messages.add_message(
            request, messages.SUCCESS,
            "Draft deleted succesfully!",
            extra_tags="alert-success"
        )
        return redirect(reverse('index'))

    # If 'GET' method
    context = {
        'recipe': recipe,
    }
    return render(request, 'catalog/recipe_delete.html', context)


class MyRecipes(LoginRequiredMixin, ListView):
    """
    Shows list of authenticated user's recipes with status 'published'.
    """
    model = Recipe
    context_object_name = 'recipes_list'
    template_name = 'catalog/recipes_list.html'
    paginate_by = 10
    allow_empty = True

    extra_context = {
        'title': 'My recipes'
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            status=Recipe.STATUS_PUBLISHED, author=self.request.user)
        return queryset


class MyDrafts(LoginRequiredMixin, ListView):
    """
    Shows list of authenticated user's recipes with status 'draft'.
    """
    model = Recipe
    context_object_name = 'recipes_list'
    template_name = 'catalog/recipes_list.html'
    paginate_by = 10
    allow_empty = True

    extra_context = {
        'title': 'My drafts'
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            status=Recipe.STATUS_DRAFT, author=self.request.user)
        return queryset


class DraftDetail(DetailView):
    """
    Shows details of selected recipe with status 'draft'.
    """
    model = Recipe
    context_object_name = 'recipe'
    template_name = 'catalog/draft_detail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('categories')
        return queryset

    def get_object(self, queryset=None):
        """
        Return the object the view is displaying.
        """
        obj = super().get_object(queryset)

        # check whether user is author of the recipe
        if obj.author != self.request.user:
            raise PermissionDenied()

        return obj


class MyFavourites(LoginRequiredMixin, ListView):
    context_object_name = 'favourites_list'
    template_name = 'catalog/favourites_list.html'
    paginate_by = 10
    allow_empty = True

    extra_context = {
        'title': 'Favourite recipes'
    }

    def get_queryset(self):
        user = self.request.user
        queryset = Favourite.objects\
            .select_related('recipe')\
            .filter(user=user)\
            .order_by('-timestamp')
        # queryset = Recipe.objects.filter(favourite__user=user)
        return queryset

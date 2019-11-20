from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.urls import reverse

import json
from datetime import datetime

from catalog.forms import (
    RecipeForm, IngredientFormSet, DirectionFormSet, RecipePhotoForm)
from catalog.models import Recipe, Category


class IndexView(TemplateView):
    template_name = 'catalog/index.html'


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
            ingredients = [{'desc': form.cleaned_data.get('desc')}
                           for form in ingredient_formset
                           if form.cleaned_data.get('desc') is not None]
            ingredients = json.dumps(ingredients)

            # Dumping direction_formset into json string.
            directions = [{'desc': form.cleaned_data.get('desc')}
                          for form in direction_formset
                          if form.cleaned_data.get('desc') is not None]
            directions = json.dumps(directions)

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

    if request.method == 'POST':
        recipe.status = Recipe.STATUS_PUBLISHED
        recipe.pub_date = datetime.now()
        recipe.save()
        return redirect(recipe)

    # If 'GET' method
    context = {
        'recipe': recipe,
    }
    return render(request, 'catalog/recipe_publish.html', context)


class RecipeDetail(DetailView):
    """
    View showing details of selected recipe.
    If recipe has status 'draft', only author has access.
    """
    model = Recipe
    context_object_name = 'recipe'

    def get_object(self, queryset=None):
        """
        Return the object the view is displaying.
        """
        obj = super().get_object(queryset)

        # check if draft
        if obj.status == Recipe.STATUS_DRAFT:
            # if draft, check whether user is author of the recipe
            if obj.author != self.request.user:
                raise PermissionDenied()
        return obj


class RecipesByCategoryList(ListView):
    """
    Shows list of published recipes in selected category.
    """
    model = Recipe
    context_object_name = 'recipes_list'
    template_name = 'catalog/recipes_by_cat_list.html'
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
        return context


# @login_required
# @transaction.atomic  # atomic in case save_m2m() failed
# def recipe_create(request):
#     if request.method == "POST":
#         recipe_form = RecipeForm(request.POST, prefix='recipe')
#         ingredient_formset = IngredientFormSet(
#             request.POST, prefix='ingredients')
#         direction_formset = DirectionFormSet(
#             request.POST, prefix='directions')

#         if (recipe_form.is_valid()
#                 and ingredient_formset.is_valid()
#                 and direction_formset.is_valid()):
#             # Create Recipe object. commit = False since we need to manually
#             # set Author field before saving to db.
#             recipe = recipe_form.save(commit=False)
#             recipe.author = request.user

#             # Dumping ingredient_formset into json string.
#             # Create list of dictionaries since such format can be used
#             # as formset initial in Recipe editing view.
#             ingredients = [{'desc': form.cleaned_data.get('desc')}
#                            for form in ingredient_formset
#                            if form.cleaned_data.get('desc') is not None]
#             ingredients = json.dumps(ingredients)

#             # Dumping direction_formset into json string.
#             directions = [{'desc': form.cleaned_data.get('desc')}
#                           for form in direction_formset
#                           if form.cleaned_data.get('desc') is not None]
#             directions = json.dumps(directions)

#             # Set ingredients and directions to respective Recipe fields
#             # and save object to db.
#             recipe.ingredients = ingredients
#             recipe.directions = directions
#             recipe.save()

#             # Since earlier was used commit=False, we need to save m2m
#             # relations manually.
#             recipe_form.save_m2m()

#             return redirect(reverse('recipe_edit', kwargs={'pk': recipe.pk}))
#     else:
#         recipe_form = RecipeForm(prefix='recipe')
#         ingredient_formset = IngredientFormSet(prefix='ingredients')
#         direction_formset = DirectionFormSet(prefix='directions')

#     context = {
#         'recipe_form': recipe_form,
#         'ingredients_formset': ingredient_formset,
#         'directions_formset': direction_formset,
#     }
#     return render(request, 'catalog/recipe_create.html', context)

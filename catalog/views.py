from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import PermissionDenied

import json

from catalog.forms import RecipeForm, IngredientFormSet, DirectionFormSet
from catalog.models import Recipe


class IndexView(TemplateView):
    template_name = 'catalog/index.html'


@login_required
@transaction.atomic  # atomic in case save_m2m() failed
def recipe_create(request):
    if request.method == "POST":
        recipe_form = RecipeForm(request.POST, prefix='recipe')
        ingredient_formset = IngredientFormSet(
            request.POST, prefix='ingredients')
        direction_formset = DirectionFormSet(
            request.POST, prefix='directions')

        if (recipe_form.is_valid()
                and ingredient_formset.is_valid()
                and direction_formset.is_valid()):
            # Create Recipe object. commit = False since we need to manually
            # set Author field before saving to db.
            recipe = recipe_form.save(commit=False)
            recipe.author = request.user

            # Dumping ingredient_formset into json string.
            # Create list of dictionaries since such format can be used
            # as formset initial in Recipe editing view.
            ingredients = [{'desc': form.cleaned_data.get('desc')}
                           for form in ingredient_formset
                           if form.cleaned_data.get('desc') is not None]
            ingredients = json.dumps(ingredients)

            # Dumping direction_formset into json string.
            directions = [{'desc': form.cleaned_data.get('desc')}
                          for form in direction_formset
                          if form.cleaned_data.get('desc') is not None]
            directions = json.dumps(directions)

            # Set ingredients and directions to respective Recipe fields
            # and save object to db.
            recipe.ingredients = ingredients
            recipe.directions = directions
            recipe.save()

            # Since earlier was used commit=False, we need to save m2m
            # relations manually.
            recipe_form.save_m2m()

            return redirect(recipe)
    else:
        recipe_form = RecipeForm(prefix='recipe')
        ingredient_formset = IngredientFormSet(prefix='ingredients')
        direction_formset = DirectionFormSet(prefix='directions')

    context = {
        'recipe_form': recipe_form,
        'ingredients_formset': ingredient_formset,
        'directions_formset': direction_formset,
    }
    return render(request, 'catalog/recipe_create.html', context)


class RecipeDetail(DetailView):
    model = Recipe
    context_object_name = 'recipe'

    def get_object(self, queryset=None):
        '''
        Return the object the view is displaying.

        If recipe has status 'draft', only author has access.
        '''
        obj = super().get_object(queryset)

        # check if draft
        if obj.status == Recipe.STATUS_DRAFT:
            # if draft, check whether user is author of the recipe
            if obj.author != self.request.user:
                raise PermissionDenied()
        return obj

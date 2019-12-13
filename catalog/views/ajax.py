""" Views for ajax requests """

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import HttpResponse, JsonResponse


from catalog.models import Recipe, Category, Favourite


def favourite_view(request, pk):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    recipe = get_object_or_404(Recipe, pk=pk, status=Recipe.STATUS_PUBLISHED)
    favourite, created = Favourite.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )
    if created:
        return JsonResponse({'created': True})
    else:
        favourite.delete()
        return JsonResponse({'created': False})

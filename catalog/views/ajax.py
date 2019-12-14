""" Views for ajax requests """

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse


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

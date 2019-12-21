""" Views for ajax requests """

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseNotAllowed


from catalog.models import Recipe, Category, Favourite
from catalog.forms import CommentForm


def favourite_view(request, pk):
    if not request.method == "GET":
        return HttpResponseNotAllowed(['GET'])
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


def add_comment_view(request, pk):
    if not request.method == "POST":
        return HttpResponseNotAllowed(['POST'])
    if not request.user.is_authenticated:
        raise PermissionDenied()

    recipe = get_object_or_404(Recipe, pk=pk, status=Recipe.STATUS_PUBLISHED)

    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.user = request.user
        comment.recipe = recipe
        comment.save()
        return JsonResponse({'success': True,
                             'comment': {'title': str(comment),
                                         'text': str(comment.text)}
                             })

    return JsonResponse({'success': False})

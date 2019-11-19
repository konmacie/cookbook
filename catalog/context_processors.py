from catalog.models import Recipe, Category


def latest_recipes(request):
    '''
    Return 5 most recent recipes
    '''
    recipes = Recipe.objects\
        .filter(status=Recipe.STATUS_PUBLISHED)\
        .select_related('author')[:5]
    return {'latest_recipes': recipes}


def all_categories(request):
    categories = Category.objects.all()
    return {'all_categories': categories}

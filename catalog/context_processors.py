from catalog.models import Recipe, Category


def latest_recipes(request):
    '''
    Return 10 most recent recipes
    Not used, since recent recipes showed only in index. No need for this.
    '''
    recipes = Recipe.objects\
        .filter(status=Recipe.STATUS_PUBLISHED)\
        .select_related('author')[:10]
    return {'latest_recipes': recipes}


def all_categories(request):
    categories = Category.objects.all()
    return {'all_categories': categories}

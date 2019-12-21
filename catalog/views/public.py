""" Views available without authentication """

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, ListView
from django.db.models import Count
from django.contrib.auth.models import User


from catalog.models import Recipe, Category, Favourite
from catalog.forms import CommentForm


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
            .prefetch_related('comments__user')\
            .annotate(like_count=Count('favourite'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add comments to context
        # comments = self.object.comments.select_related('author')
        # context['comments'] = comments

        # if user authenticated...
        if self.request.user.is_authenticated:

            # ... check if user liked recipe
            is_liked = Favourite.objects.filter(
                recipe=self.object,
                user=self.request.user
            ).exists()
            context['is_liked'] = is_liked

            # ... add comment form to context
            comment_form = CommentForm()
            context['comment_form'] = comment_form

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


class RecipesByUser(ListView):
    """
    Shows recipes created by selected user
    """
    model = Recipe
    context_object_name = 'recipes_list'
    template_name = 'catalog/recipes_list.html'
    paginate_by = 10
    allow_empty = True

    def get_queryset(self):
        queryset = super().get_queryset()

        self.selected_user = get_object_or_404(User, pk=self.kwargs.get('pk'))

        queryset = queryset.filter(
            status=Recipe.STATUS_PUBLISHED,
            author=self.selected_user
        )

        return queryset

    def get_context_data(self, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        title = "Recipes by: {}".format(self.selected_user)
        context['title'] = title
        return context

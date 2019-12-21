from django.urls import path, include
from catalog import views

urlpatterns = [
    # PUBLIC VIEWS
    path('', views.public.IndexView.as_view(), name='index'),
    path('recipe/<int:pk>/', views.public.RecipeDetail.as_view(),
         name='recipe_detail'),
    path('category/<slug:slug>/', views.public.RecipesByCategoryList.as_view(),
         name='recipes_by_category'),
    path('newest/', views.public.RecipesNewest.as_view(),
         name='recipes_newest'),
    path('popular/', views.public.RecipesPopular.as_view(),
         name='recipes_popular'),
    path('recipes/by/<int:pk>/', views.public.RecipesByUser.as_view(),
         name='recipes_by_user'),

    # USER VIEWS
    path('recipe/new/', views.user.recipe_create_draft, name='recipe_create'),
    path('recipes/my/published/', views.user.MyRecipes.as_view(),
         name='my_recipes'),
    path('recipes/my/drafts/', views.user.MyDrafts.as_view(),
         name='my_drafts'),
    path('draft/<int:pk>/', views.user.DraftDetail.as_view(),
         name='draft_detail'),
    path('recipes/my/favourite/', views.user.MyFavourites.as_view(),
         name='my_favourites'),
    path('recipe/<int:pk>/edit/', views.user.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/publish/', views.user.recipe_publish,
         name='recipe_publish'),
    path('recipe/<int:pk>/delete/', views.user.recipe_delete,
         name='recipe_delete'),

    # AJAX
    path('recipe/<int:pk>/favourite/', views.ajax.favourite_view,
         name='favourite_toggle'),
    path('recipe/<int:pk>/add_comment/', views.ajax.add_comment_view,
         name='add_comment'),
]

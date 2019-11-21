from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('recipe/new/', views.recipe_create_draft, name='recipe_create'),
    path('recipe/<int:pk>/', views.RecipeDetail.as_view(),
         name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/publish/', views.recipe_publish,
         name='recipe_publish'),
    path('category/<slug:slug>/', views.RecipesByCategoryList.as_view(),
         name='recipes_by_category'),
    path('newest/', views.RecipesNewest.as_view(), name='recipes_newest'),
    path('recipes/my/published/', views.MyRecipes.as_view(),
         name='my_recipes'),
    path('recipes/my/drafts/', views.MyDrafts.as_view(),
         name='my_drafts'),
]

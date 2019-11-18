from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('recipe/new/', views.recipe_create_draft, name='recipe_create'),
    path('recipe/<int:pk>/', views.RecipeDetail.as_view(),
         name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
]

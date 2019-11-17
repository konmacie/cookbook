from django.contrib import admin
from catalog.models import Recipe, Category


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'pub_date', 'edit_date']


admin.site.register(Category)
admin.site.register(Recipe, RecipeAdmin)

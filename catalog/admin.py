from django.contrib import admin
from catalog.models import Recipe, Category


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'pub_date', 'edit_date']


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Recipe, RecipeAdmin)

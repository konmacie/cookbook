from django.contrib import admin
from catalog.models import Recipe, Category, Comment


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'pub_date', 'edit_date']


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'pub_date']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Comment, CommentAdmin)

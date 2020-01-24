from django import forms
from django.core.exceptions import ValidationError
from catalog.models import Recipe, Category, Comment


class RecipeForm(forms.ModelForm):
    '''
    Form used to create/edit Recipe model.
    Has only 'title', 'categories' and 'description' fields.
    'Directions' and 'Ingredients' will be created using different formsets
    and set to model fields in view.
    '''
    class Meta:
        model = Recipe
        fields = ('title', 'categories', 'description', )

    # fields
    categories = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Category.objects.all(),
        required=True,
    )


class RecipePhotoForm(forms.Form):
    photo = forms.ImageField(required=False)

    def clean_photo(self):
        image = self.cleaned_data.get('photo', None)
        if image:
            if image.size > 2*1024*1024:  # 2MB
                raise ValidationError("Image too large! Allowed up tp 1MB.")
            return image
        return None


class IngredientForm(forms.Form):
    desc = forms.CharField(min_length=3, max_length=64, required=False)


IngredientFormSet = forms.formset_factory(
    IngredientForm, extra=0, min_num=1, validate_min=False,
)


class DirectionForm(forms.Form):
    desc = forms.CharField(min_length=6, max_length=254,
                           required=False, widget=forms.Textarea)


DirectionFormSet = forms.formset_factory(
    DirectionForm, extra=0, min_num=1, validate_min=False,
)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    text = forms.CharField(min_length=10, max_length=250,
                           required=True, widget=forms.Textarea)

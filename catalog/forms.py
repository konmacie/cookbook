from django import forms
from django.core.exceptions import ValidationError
from catalog.models import Recipe, Category


class RecipeForm(forms.ModelForm):
    '''
    Form used to create/edit Recipe model.
    Has only 'title' and 'categories' fields.
    'Directions' and 'Ingredients' will be created using different formsets
    and set to model fields in view.
    '''
    class Meta:
        model = Recipe
        fields = ('title', 'categories', )

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
    desc = forms.CharField(min_length=3, max_length=64)


IngredientFormSet = forms.formset_factory(
    IngredientForm, extra=0, min_num=1, validate_min=True,
)


class DirectionForm(forms.Form):
    desc = forms.CharField(min_length=6, max_length=254)


DirectionFormSet = forms.formset_factory(
    DirectionForm, extra=0, min_num=1, validate_min=True
)

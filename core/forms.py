from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Box, Order, Product


class CrispyFormMixin:
    submit_label = 'Save'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', self.submit_label, css_class='btn btn-primary px-4'))


class ProductForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'length', 'width', 'height', 'weight']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Wireless Mouse'}),
        }


class BoxForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Box
        fields = ['name', 'length', 'width', 'height', 'max_weight', 'cost']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Small Mailer Box'}),
        }


class OrderForm(CrispyFormMixin, forms.ModelForm):
    submit_label = 'Create Order & Recommend Box'
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Order
        fields = ['customer_name', 'products', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields.pop('status')

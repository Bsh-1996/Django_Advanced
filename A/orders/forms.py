from django import forms


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=9)


class CoupanApplyForm(forms.Form):
    code = forms.CharField()
    
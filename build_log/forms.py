from django import forms
from .models import ItemOut

class ItemOutForm(forms.ModelForm):
    class Meta:
        model = ItemOut
        fields = "__all__"

        widgets = {
            "out_date": forms.TextInput(attrs={'class':'form-control','type':'date'}),
            "sparepart": forms.Select(attrs={'class':'form-control'}),
            "build_log": forms.Select(attrs={'class':'form-control'}),
            "stock_out": forms.TextInput(attrs={'class':'form-control','type':'number'}),
            "personal_use": forms.TextInput(attrs={'class':'form-check-input','type':'checkbox'}),
            "notes": forms.Textarea(attrs={'class':'form-control'}),
        }

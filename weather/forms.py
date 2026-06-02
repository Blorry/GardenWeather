from django import forms
from .models import GardenPlot


class GardenPlotForm(forms.ModelForm):
    class Meta:
        model = GardenPlot
        fields = ['name', 'region', 'cultures', 'area']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'cultures': forms.CheckboxSelectMultiple(),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
        labels = {
            'name': 'Название участка',
            'region': 'Регион',
            'cultures': 'Культуры',
            'area': 'Площадь, сот.',
        }

    def clean_area(self):
        area = self.cleaned_data['area']
        if area <= 0:
            raise forms.ValidationError('Площадь должна быть больше нуля.')
        if area > 1000:
            raise forms.ValidationError('Площадь не может превышать 1000 соток.')
        return area

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('Название должно содержать минимум 2 символа.')
        return name
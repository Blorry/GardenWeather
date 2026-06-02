from django import forms
from .models import GardenPlot, Planting
from django.utils import timezone
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class GardenPlotForm(forms.ModelForm):
    class Meta:
        model = GardenPlot
        fields = ['name', 'region', 'soil_type', 'area']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'soil_type': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }
        labels = {
            'name': 'Название участка',
            'region': 'Регион',
            'soil_type': 'Тип почвы на участке',
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
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'}),
        label='Email',
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['username'].label = 'Логин'
        self.fields['username'].help_text = (
            'От 3 до 30 символов: латинские буквы, цифры, символы _ или -.'
        )
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повтор пароля'

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not USERNAME_PATTERN.match(username):
            raise forms.ValidationError(
                'Логин должен содержать 3–30 символов: только латинские буквы, цифры, _ или -.'
            )
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class PlantingForm(forms.ModelForm):
    class Meta:
        model = Planting
        fields = ['culture', 'status', 'planted_date']
        widgets = {
            'culture': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'planted_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'culture': 'Культура',
            'status': 'Статус',
            'planted_date': 'Дата посадки',
        }

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get('status')
        planted_date = cleaned.get('planted_date')
        if status == Planting.Status.PLANTED:
            if not planted_date:
                cleaned['planted_date'] = timezone.now().date()  # не указали — считаем сегодня
            elif planted_date > timezone.now().date():
                self.add_error('planted_date', 'Дата посадки не может быть в будущем.')
        else:
            cleaned['planted_date'] = None  # «планируется» — даты посадки нет
        return cleaned
from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing  # Модель, с которой связана форма
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']  # Поля формы
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),  # Настройка виджета для текстового поля
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'starting_bid': 'Начальная ставка',
            'image_url': 'URL изображения (опционально)',
            'category': 'Категория',
        }

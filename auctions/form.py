from django import forms
from .models import Listing
from .models import Bid


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing  # Модель, с которой связана форма
        fields = ['title', 'description', 'starting_bid',
                  'image_url', 'category']  # Поля формы
        widgets = {
            # Настройка виджета для текстового поля
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'starting_bid': 'Начальная ставка',
            'image_url': 'URL изображения (опционально)',
            'category': 'Категория',
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']
        labels = {
            'bid_amount': 'Your Bid',
        }

from django import forms
from .models import Listing, Bid, Comment


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing 
        fields = ['title', 'description', 'starting_bid',
                  'image_url', 'category']  
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
        labels = {
            'title': 'Title',
            'description': 'Description',
            'starting_bid': 'Starting Bid',
            'image_url': 'Image URL (optional)',
            'category': 'Category',
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_amount']
        labels = {
            'bid_amount': 'Your Bid',
        }
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
        }
        labels = {
            'content': '',
        }

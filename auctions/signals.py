from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bid, Listing

@receiver(post_save, sender=Bid)
def update_listing_current_price(sender, instance, **kwargs):
    
    listing = instance.listing
    
    highest_bid = listing.bids.order_by('-bid_amount').first()
    if highest_bid:
        listing.current_price = highest_bid.bid_amount
        listing.save()

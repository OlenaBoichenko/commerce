from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        'Listing', related_name="watched_by", blank=True)

#Model for listing
class Listing(models.Model):
    title = models.CharField(max_length=255)  
    description = models.TextField()  
    starting_bid = models.DecimalField(
        max_digits=10, decimal_places=2)  
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100) 
    created_at = models.DateTimeField(
        auto_now_add=True)  
    is_active = models.BooleanField(default=True) 
    owner = models.ForeignKey(
        'User', on_delete=models.CASCADE) 

    def __str__(self):
        return self.title  

#Model for auction
class Bid(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")  
    bid_amount = models.DecimalField(
        max_digits=10, decimal_places=2) 
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_time = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Bid of ${self.bid_amount} by {self.bidder.username} on {self.listing.title}"

#Model for comments
class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField()  
    created_at = models.DateTimeField(
        auto_now_add=True)  

    def __str__(self):
        return f"Comment by {self.user.username} on {self.listing.title}"

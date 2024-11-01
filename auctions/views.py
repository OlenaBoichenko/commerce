from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .form import ListingForm, BidForm, CommentForm
from .models import Listing, Bid
from django.contrib import messages
from .models import User
from django.db.models import Count


def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, 'auctions/index.html', {
        'listings': listings
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.owner = request.user  
            new_listing.current_price = new_listing.starting_bid
            new_listing.save()
            
            return redirect('index')
    else:
        form = ListingForm()  
    
    return render(request, 'auctions/create_listing.html', {'form': form})


def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)
    is_in_watchlist = False
    current_bid = listing.starting_bid
    is_winner = False
    comments = listing.comments.all()

    if listing.bids.exists():
        current_bid = listing.bids.latest('bid_time').bid_amount

    if request.user.is_authenticated:
        is_in_watchlist = listing in request.user.watchlist.all()
        
        if not listing.is_active:
            highest_bid = listing.bids.order_by('-bid_amount').first()
            if highest_bid and highest_bid.bidder == request.user:
                is_winner = True

    if request.method == "POST" and 'place_bid' in request.POST:
        form = BidForm(request.POST)
        comment_form = CommentForm()
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']

            if bid_amount < listing.starting_bid:
                messages.error(
                    request, "Bid must be at least as large as the starting bid.")
            elif listing.bids.exists() and bid_amount <= listing.bids.latest('bid_time').bid_amount:
                messages.error(
                    request, "Bid must be greater than the current highest bid.")
            else:
                bid = form.save(commit=False)
                bid.listing = listing
                bid.bidder = request.user
                bid.save()
                listing.current_price = bid_amount
                listing.save()
                messages.success(request, "Your bid was successfully placed!")
                return redirect('listing', id=listing.id)
    elif request.method == "POST" and 'add_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        form = BidForm()
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.listing = listing
            comment.user = request.user
            comment.save()
            messages.success(request, "Your comment was successfully added!")
            return redirect('listing', id=listing.id)
    else:
        form = BidForm()
        comment_form = CommentForm()

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'is_in_watchlist': is_in_watchlist,
        'form': form,
        'current_bid': current_bid,  
        'is_winner': is_winner, 
        'comments': comments,
        'comment_form': comment_form,
    })
    
def categories(request):
    categories = Listing.objects.values('category').annotate(count=Count('category')).filter(is_active=True)
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })

def category_listings(request, category_name):
    listings = Listing.objects.filter(category=category_name, is_active=True)
    return render(request, 'auctions/category_listings.html', {
        'category_name': category_name,
        'listings': listings
    })


@login_required
def add_to_watchlist(request, id):
    listing = get_object_or_404(Listing, id=id)
    user = request.user
    user.watchlist.add(listing)
    return redirect('listing', id=id)


@login_required
def remove_from_watchlist(request, id):
    listing = get_object_or_404(Listing, id=id)
    user = request.user
    user.watchlist.remove(listing)
    return redirect('index')


@login_required
def watchlist(request):
    user = request.user
    watchlist_items = user.watchlist.all()
    return render(request, 'auctions/watchlist.html', {'watchlist_items': watchlist_items})


@login_required
def close_auction(request, id):
    listing = get_object_or_404(Listing, id=id)

    if request.user != listing.owner:
        messages.error(request, "You are not authorized to close this auction.")
        return redirect('listing', id=id)

    listing.is_active = False
    listing.save()

    highest_bid = listing.bids.order_by('-bid_amount').first()
    if highest_bid:
        messages.success(request, f"The auction is closed. The winner is {highest_bid.bidder.username} with a bid of ${highest_bid.bid_amount}.")
    else:
        messages.info(request, "The auction is closed with no bids placed.")

    return redirect('listing', id=id)

@login_required
def user_profile(request):
    user_bids = Bid.objects.filter(bidder=request.user).select_related('listing')
    
    listings_with_user_bids = {bid.listing for bid in user_bids}

    listings_data = []
    for listing in listings_with_user_bids:
        highest_bid = listing.bids.order_by('-bid_amount').first() if listing.bids.exists() else None
        is_winner = highest_bid and highest_bid.bidder == request.user
        listings_data.append({
            'listing': listing,
            'is_winner': is_winner,
            'highest_bid': highest_bid,
        })

    return render(request, 'auctions/user_profile.html', {
        'listings_data': listings_data,
    })

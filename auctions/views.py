from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .form import ListingForm
from .models import Listing, Bid
from django.contrib import messages
from .form import BidForm

from .models import User


def index(request):
    # Отбираем только активные объявления
    listings = Listing.objects.filter(is_active=True)
    return render(request, 'auctions/index.html', {
        'listings': listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
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
            # Сохраняем новое объявление в базе данных
            new_listing = form.save(commit=False)
            new_listing.owner = request.user  # Привязываем объявление к текущему пользователю
            new_listing.current_price = new_listing.starting_bid
            new_listing.save()
            # Перенаправление на главную страницу после успешного создания
            return redirect('index')
    else:
        form = ListingForm()  # Пустая форма для GET-запроса
    # Рендерим шаблон с формой
    return render(request, 'auctions/create_listing.html', {'form': form})


def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)
    is_in_watchlist = False
    # По умолчанию текущая ставка - начальная ставка
    current_bid = listing.starting_bid

    # Проверяем, есть ли ставки, и устанавливаем текущую наивысшую ставку
    if listing.bids.exists():
        current_bid = listing.bids.latest('bid_time').bid_amount

    if request.user.is_authenticated:
        is_in_watchlist = listing in request.user.watchlist.all()

    # Обработка подачи ставки
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']
            # Проверка на минимальную ставку
            if bid_amount < listing.starting_bid:
                messages.error(
                    request, "Bid must be at least as large as the starting bid.")
            elif listing.bids.exists() and bid_amount <= listing.bids.latest('bid_time').bid_amount:
                messages.error(
                    request, "Bid must be greater than the current highest bid.")
            else:
                # Создание новой ставки
                bid = form.save(commit=False)
                bid.listing = listing
                bid.bidder = request.user
                bid.save()
                # Обновляем текущую цену объявления
                listing.current_price = bid_amount
                listing.save()
                messages.success(request, "Your bid was successfully placed!")
                return redirect('listing', id=listing.id)
    else:
        form = BidForm()

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'is_in_watchlist': is_in_watchlist,
        'form': form,
        'current_bid': current_bid  # Передаем текущую ставку в шаблон
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
    # Получаем все объявления из избранного текущего пользователя
    watchlist_items = user.watchlist.all()
    return render(request, 'auctions/watchlist.html', {'watchlist_items': watchlist_items})

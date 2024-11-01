from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing/', views.create_listing, name='create_listing'),
    path("listing/<int:id>/", views.listing_detail, name="listing"),
    path("listing/<int:id>/add_to_watchlist/", views.add_to_watchlist, name="add_to_watchlist"),     path("listing/<int:id>/remove_from_watchlist/", views.remove_from_watchlist, name="remove_from_watchlist"), 
    path("watchlist/", views.watchlist, name="watchlist"),  
    path("listing/<int:id>/close_auction/", views.close_auction, name="close_auction"),
    path("profile/", views.user_profile, name="user_profile"),  
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category_name>/", views.category_listings, name="category_listings"),
]

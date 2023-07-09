from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create-listing", views.create_listing, name="create-listing"),
    path("listing/<str:listing>", views.view_listing, name="view-listing"),
    path("listing/close/<str:listing>", views.close_listing, name="close-listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/add/<str:listing>", views.watchlist_add, name="watchlist-add"),
    path("watchlist/remove/<str:listing>", views.watchlist_remove, name="watchlist-remove"),
    path("category", views.category_list, name="category-list"),
    path("category/<str:category>", views.category, name="category")
]

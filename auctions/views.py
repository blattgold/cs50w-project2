from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User
from .models import AuctionListing
from .models import Bid
from .models import Comment

from .utils import get_highest_bid

class CreateListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=64)
    description = forms.CharField(label="Description", max_length=256)
    starting_bid = forms.DecimalField(decimal_places=2)
    image = forms.URLField(required=False)
    category = forms.CharField(label="Category", max_length=64, required=False)
    
class BidOnItemForm(forms.Form):
    bid = forms.DecimalField(decimal_places=2)

class CommentForm(forms.Form):
    content = forms.CharField(label="leave a comment", max_length=256, widget=forms.Textarea)

def index(request):
    listings = AuctionListing.objects.values("title",
                                             "description",
                                             "image",
                                             "category")
    listings_list = [entry for entry in listings]

    for i, price in enumerate(AuctionListing.objects.values("starting_bid")):
        listings_list[i]["highest_bid"] = round(get_highest_bid(listings_list[i]["title"]).amount / 100, 2)

    for i, active in enumerate(AuctionListing.objects.values("winner")):
        listings_list[i]["closed"] = AuctionListing.objects.get(title=listings_list[i]["title"]).winner is not None

    return render(request, "auctions/index.html", {
        "listings": listings_list 
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

@login_required
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

@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image = request.POST["image"]
        category = request.POST["category"]
        author = request.user

        starting_bid = int (float(starting_bid) * 100)

        AuctionListing.objects.create(title=title,
                                      description=description,
                                      starting_bid=starting_bid,
                                      image=image,
                                      category=category,
                                      author=author)
        
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create-listing.html",{
            "form": CreateListingForm()
        })

def view_listing(request, listing):
    if request.method == "POST" and request.user.is_authenticated:
        if "bid" in request.POST.keys():
            bid_amt = int(float(request.POST["bid"]) *100)

            highest_bid = get_highest_bid(listing)

            if bid_amt > highest_bid.amount:
                bid = Bid(author=request.user,
                          amount=bid_amt,
                          listing=AuctionListing.objects.get(title=listing))
                bid.save()
            else:
                messages.error(request, "Your bid must be higher than the previous bid")

            return HttpResponseRedirect(request.path_info, 
                                        listing)
        elif "content" in request.POST.keys():
            content = request.POST["content"]
            listing_object = AuctionListing.objects.get(title=listing)

            Comment.objects.create(author=request.user,
                                   listing=listing_object,
                                   content=content)

            return HttpResponseRedirect(request.path_info, 
                                        listing)

    elif not AuctionListing.objects.filter(title=listing):
        return render(request, "auctions/listing-not-found.html", {
            "listing": listing
        })
    else:
        listing = AuctionListing.objects.get(title=listing)

        title = listing.title
        description = listing.description
        category = listing.category
        author = listing.author
        image = listing.image

        highest_bid = get_highest_bid(title)

        if AuctionListing.objects.get(title=title).winner is not None:
            messages.success(request, "This auction has been closed.")

        if request.user.is_authenticated:
            on_watchlist = listing not in AuctionListing.objects.filter(watchlist=request.user) 
            if request.user == AuctionListing.objects.get(title=title).winner:
                messages.success(request, "Congratulations! You won this auction!")
        else:
            on_watchlist = False

        comments = Comment.objects.filter(listing=listing)

        return render(request, "auctions/listing.html",{
            "title": title,
            "description": description,
            "category": category,
            "author": author,
            "image": image,
            "bid_form": BidOnItemForm,
            "highest_bid": round(highest_bid.amount / 100, 2),
            "highest_bidder": highest_bid.author,
            "on_watchlist": on_watchlist,
            "comment_form": CommentForm,
            "comments": comments
        })

@login_required
def close_listing(request, listing):
    listing_object = AuctionListing.objects.get(title=listing)
    if request.user == listing_object.author:
        listing_object.winner = get_highest_bid(listing).author
        listing_object.save()
    return HttpResponseRedirect(reverse("view-listing", kwargs={'listing': listing}))

@login_required
def watchlist(request):
    listings = AuctionListing.objects.values("title",
                                             "description",
                                             "image",
                                             "category") \
                                     .filter(watchlist=request.user)
    listings_list = [entry for entry in listings]

    for i, price in enumerate(AuctionListing.objects.values("starting_bid").filter(watchlist=request.user)):
        listings_list[i]["highest_bid"] = round(get_highest_bid(listings_list[i]["title"]).amount / 100, 2)

    return render(request, "auctions/watchlist.html", {
        "watchlist": listings_list
    })

@login_required
def watchlist_add(request, listing):
    listing_object = AuctionListing.objects.get(title=listing)
    if listing_object not in AuctionListing.objects.filter(watchlist=request.user):
        listing_object.watchlist.add(request.user)

    return HttpResponseRedirect(reverse("watchlist"))

@login_required
def watchlist_remove(request, listing):
    listing_object = AuctionListing.objects.get(title=listing)
    if listing_object in AuctionListing.objects.filter(watchlist=request.user):
        listing_object.watchlist.remove(request.user)

    return HttpResponseRedirect(reverse("watchlist"))

def category_list(request):
    category_list_raw = AuctionListing.objects.values("category").filter(winner=None)

    category_list_processed = []
    for category in category_list_raw:
        if category["category"] not in category_list_processed \
           and len(category["category"]) != 0:
            category_list_processed.append(category["category"])

    return render(request, "auctions/category-list.html", {
        "categories": category_list_processed,
    })

def category(request, category):
    
    listings = AuctionListing.objects.values("title",
                                             "description",
                                             "image",
                                             "category").filter(category=category)
    listings_list = [entry for entry in listings]

    for i, price in enumerate(AuctionListing.objects.values("starting_bid").filter(category=category)):
        listings_list[i]["highest_bid"] = round(get_highest_bid(listings_list[i]["title"]).amount / 100, 2)

    for i, active in enumerate(AuctionListing.objects.values("winner").filter(category=category)):
        listings_list[i]["closed"] = AuctionListing.objects.get(title=listings_list[i]["title"]).winner is not None

    return render(request, "auctions/category.html", {
        "listings": listings_list,
        "category": category
    })

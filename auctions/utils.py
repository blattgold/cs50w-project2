from .models import Bid
from .models import AuctionListing

def get_highest_bid(listing):

    listing_object = AuctionListing.objects.get(title=listing)
    highest_bid = Bid(listing=listing_object,
                      amount=listing_object.starting_bid,
                      author=listing_object.author)

    for current_bid in Bid.objects.filter(listing=listing_object):
        if current_bid.amount > highest_bid.amount:
            highest_bid = current_bid

    return highest_bid


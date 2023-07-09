from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    starting_bid = models.IntegerField()
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64,
                                default="no category") 
    author = models.ForeignKey(User,
                               models.CASCADE,
                               related_name="author")
    watchlist = models.ManyToManyField(User,
                                       related_name="watchlist",
                                       null=True)
    winner = models.ForeignKey(User,
                               models.CASCADE,
                               related_name="winner",
                               null=True,
                               unique=False)

    def __str__(self):
        return self.title

class Bid(models.Model):
    author = models.ForeignKey(User,
                               models.CASCADE,
                               related_name="bids")
    listing = models.ForeignKey(AuctionListing,
                                models.CASCADE,
                                related_name="bids")
    amount = models.IntegerField()

    def __str__(self):
        return f"listing: {self.listing}, {self.author}: {self.amount}"

class Comment(models.Model):
    author = models.ForeignKey(User,
                               models.CASCADE,
                               related_name="comment_author")
    listing = models.ForeignKey(AuctionListing,
                                models.CASCADE,
                                related_name="listing")
    content = models.CharField(max_length=256)

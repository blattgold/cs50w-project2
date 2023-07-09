from django.contrib import admin

from .models import AuctionListing
from .models import Bid
from .models import User
from .models import Comment
# Register your models here.

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "author"]

class BidAdmin(admin.ModelAdmin):
    list_display = ["listing", "author", "amount"]

class CommentAdmin(admin.ModelAdmin):
    list_display = ["listing", "author", "content"]

admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(User)

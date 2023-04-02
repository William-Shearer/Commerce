from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db import models


class User(AbstractUser):
    """
    The fields I want to use are redefined here. These are default attributes of AbstractUser,
    however, I want to make them obligatory and also limit the number of character in the CharFields.
    This is straightforward enough.
    """    
    username = models.CharField(max_length = 50, blank = False, null = False, primary_key = True)
    email = models.EmailField(blank = False, null = False)
    first_name = models.CharField(max_length = 50, blank = False, null = False)
    last_name = models.CharField(max_length = 50, blank = False, null = False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})" 


class Category(models.Model):
    """
    This is the list of categories for the items (motorcycles) that will be on the auction list.
    """
    cat_id = models.AutoField(primary_key = True)
    category = models.CharField(max_length = 50) # Add unique = True?
    
    def __str__(self):
        return f"{self.category}"
        
    
class Bike(models.Model):
    bike_id = models.AutoField(primary_key = True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name = "bike_by_category", blank = False, null = False)
    company = models.CharField(max_length = 50, blank = False, null = False)
    model = models.CharField(max_length = 50, blank = False, null = False)
    fab_year = models.IntegerField()
    description = models.TextField()
    posted_by = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "bike_by_user", blank = False, null = False)
    bike_img = models.URLField(blank = True, null = True)
    is_open = models.BooleanField(default = True)
    is_active = models.BooleanField(default = True)
    date_created = models.DateTimeField(auto_now_add = True)
    
    def clean_fab_year(self, fab_year):
        tm = datetime.now()
        this_year = int(tm.year)
        if fab_year > this_year or fab_year < 1880:
            raise ValidationError("fab_year error")
    
    def __str__(self):
        fdate = self.date_created.strftime("UTC %H:%M, %d %B, %Y")
        return f"{self.category.category} {self.company} {self.model}, {self.fab_year}, posted by {self.posted_by.username}, {fdate}"
        

class Comment(models.Model):
    comment_id = models.AutoField(primary_key = True)
    comment = models.TextField()
    bike = models.ForeignKey(Bike, on_delete = models.CASCADE, related_name = "comment_by_bike")
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "comment_by_user")
    date_posted = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        fdate = self.date_posted.strftime("UTC %H:%M, %d %B, %Y")
        return f"Coment by {self.user.username}, {fdate}"


class Bid(models.Model):
    bid_id = models.AutoField(primary_key = True)
    bid = models.DecimalField(max_digits = 9, decimal_places = 2)
    bike = models.ForeignKey(Bike, on_delete = models.CASCADE, related_name = "bid_by_bike")
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "bid_by_user")
    date_bid = models.DateTimeField(auto_now_add = True)
    
    def clean_bid(self, bid, bike):
        bike_bids = Bid.objects.filter(bike = bike)
        ordered = bike_bids.order_by("bid")
        if bid <= ordered.last().bid:
            raise ValidationError("bid too low")
            
    def clean_user(self, user, posted_by):
        if user == posted_by:
            raise ValidationError("cannot bid on own bike")
    
    def __str__(self):
        fdate = self.date_bid.strftime("UTC %H:%M, %d %B, %Y")
        return f"${self.bid} by {self.user.username} for {self.bike.company} {self.bike.model} on {fdate}"
    
    
    
    
class WatchList(models.Model):
    watch_id = models.AutoField(primary_key = True)
    bike = models.ForeignKey(Bike, on_delete = models.CASCADE, related_name = "watchlist_by_bike")
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "watchlist_by_user")
    
    def __str__(self):
        return f"{self.bike.company} {self.bike.model} watched by {self.user.username}"
        
        



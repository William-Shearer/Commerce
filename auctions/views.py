from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *


def index_reducer(select_category = None):
    if select_category == None:
        bikes = Bike.objects.filter(is_active = True).order_by("-date_created")
   
    else:
        bikes = Bike.objects.filter(is_active = True, category = Category.objects.get(category = select_category)).order_by("-date_created")
    
    last_bids = []
    for bike in bikes:
        last_bid = bike.bid_by_bike.order_by("bid").last().bid
        last_bids.append(last_bid)
        
    content = {"bikes": zip(bikes, last_bids)} #, "form": form}
    return content


def general_reducer(type_form):
    if type_form == "login":
        form = LoginForm()
    elif type_form == "register":
        form = RegisterForm()
    elif type_form == "change":
        form = ChangePasswordForm()
    elif type_form == "create":
        form = CreateBikeForm()
    content = {"form": form}
    return content    


def bikeview_reducer(bike, user):
    comments = bike.comment_by_bike.all()
    bids = bike.bid_by_bike.all().order_by("bid").exclude(user = bike.posted_by)
    form_b = BidForm() 
    form_c = CommentForm()
    on_watchlist = WatchList.objects.filter(bike = bike, user = user).exists()
    open_bid = bike.bid_by_bike.all().order_by('bid').first()
    last_bid = bids.last()
    content = { "bike": bike, 
                "comments": comments, 
                "bids": bids, 
                "form_b": form_b, 
                "form_c": form_c, 
                "on_watchlist": on_watchlist,
                "open_bid": open_bid,
                "last_bid": last_bid}
    return content
   
    
# ------------------------------------------------------------
# Views...
def index(request):
    if request.method == "GET":
        content = index_reducer()
        if not content["bikes"]:
            messages.info(request, "No bikes for auction")
        return render(request, "auctions/index.html", content)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST or None)
        
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username = username, password = password)
            
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
                
            else:
                messages.warning(request, "Invalid username and/or password.") 
                content = general_reducer("login")
            return render(request, "auctions/login.html", content)
            
        else:
            messages.warning(request, "Invalid form submission data.")
            content = general_reducer("login")
            return render(request, "auctions/login.html", content)
            
    elif request.method == "GET":
        user = request.user
        
        if user.is_authenticated:
            return redirect(reverse("index"))
            
        else:
            content = general_reducer("login")
            return render(request, "auctions/login.html", content)
    
    return redirect(reverse("index"))    


@login_required(login_url = "login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST or None)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            if password != form.cleaned_data.get("confirmation"):
                messages.warning(request, "Passwords must match.")
                return redirect(reverse("register"))
                 
            try:
                user = User.objects.create_user(    form.cleaned_data.get("username"), 
                                                    form.cleaned_data.get("email"),
                                                    password)
                user.first_name = form.cleaned_data.get("first_name")
                user.last_name = form.cleaned_data.get("last_name")
                user.save()
                
            except IntegrityError:
                messages.warning(request, "Username already taken.")
                content = general_reducer("register")
                return render(request, "auctions/register.html", content)
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return HttpResponseRedirect(reverse("index"))

    elif request.method == "GET":
        user = request.user
        if user.is_authenticated:
            return redirect(reverse("index"))
        else:
            content = general_reducer("register")
            return render(request, "auctions/register.html", content)

    return redirect(reverse("index"))


@login_required(login_url = "login")
def edituser(request):
    if request.method == "POST":
        form = EditUserForm(request.POST or None)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            user.email = form.cleaned_data.get("email")
            user.save()
            messages.success(request, "User edited")
            return redirect(reverse("index"))
       
        else:
            messages.warning("Form data invalid")
            return redirect(reverse("index"))
            
    elif request.method == "GET":
        user = request.user
        form_data = {   "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email}

        form = EditUserForm(initial = form_data)
        content = {"form": form}
        return render(request, "auctions/edituser.html", content)
        
    # Any other conditions, running back to the index is the safest bet.
    return redirect(reverse("index"))


@login_required(login_url = "login")
def changepwd(request):
    if request.method =="POST":
        form = ChangePasswordForm(request.POST or None)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            confirmation = form.cleaned_data.get("confirmation")

            if password == confirmation:
                user = request.user
                user.set_password(password)
                user.save()
                login(request, user)
                return redirect(reverse("index"))
            else:
                messages.warning(request, "Passwords do not match")
                content = general_reducer("change")
                return render(request, "auctions/changepwd.html", content)
        else:
            form = ChangePasswordForm()
            content = {"form": form, "message": "Form validation error."}
            return render(request, "auctions/changepwd.html", content)
    
    elif request.method == "GET":
        content = general_reducer("change")
        return render(request, "auctions/changepwd.html", content)
    
    return redirect(reverse("index"))


def category(request):
    if request.method == "GET":
        categories = Category.objects.all().order_by("category")
        content = {"categories": categories}
        return render(request, "auctions/category.html", content)
        
    elif request.method == "POST":
        select_category = request.POST.get("category")
        content = index_reducer(select_category)
        # Here is how to sort out if a key of the content is empty in values.
        if not content["bikes"]:
            messages.info(request, "No Bikes in Category")
        return render(request, "auctions/index.html", content)
            
    # Default run home...
    else: 
        return redirect(reverse("index"))


@login_required(login_url = "login")
def bikeview(request, bike_id):
    bike = Bike.objects.get(bike_id = bike_id)
    user = request.user
    
    if request.method == "POST":
        # The name of the button is accessed here to see if it exists. Another trick.
        if "make_bid" in request.POST:
            form = BidForm(request.POST or None)
            if form.is_valid():
                if bike.is_open == True and bike.is_active == True:
                    bid = form.cleaned_data.get("bid")
                    new_bid = Bid(bid = bid, bike = bike, user = user)
                    try:
                        new_bid.clean_bid(bid, bike)
                        new_bid.clean_user(user, bike.posted_by)
                        new_bid.save()
                    except ValidationError:
                        messages.error(request, "Sorry, that is an invalid bid.")
                        
                else:
                    messages.warning(request, "Bidding is closed")

        elif "post_comment" in request.POST:
            form = CommentForm(request.POST or None)
            if form.is_valid():
                comment = form.cleaned_data.get("comment")
                new_comment = Comment(comment = comment, bike = bike, user = user)
                if new_comment.comment != "":
                    new_comment.save()
                    
        elif "close" in request.POST:
            bike.is_open = False
            bike.save()
                        
        content = bikeview_reducer(bike, user)
        return redirect(reverse("bikeview", args = (bike_id,)), content)
    
    elif request.method == "GET":
        content = bikeview_reducer(bike, user)
        
        if content["last_bid"]:
            if content["last_bid"].user == user and not bike.is_open:
                messages.info(request, "Attention: You Win!")
                
        return render(request, "auctions/bikepage.html", content)
        
    else:
        return redirect(reverse("index"))

        
@login_required(login_url = "login")
def createbike(request):
    """
    Create bike uses a form to create a new listing. The user must be logged in.
    The model is populated by the form data, and the index screen is rendered, with the message that
    a new bike was created.
    """
    if request.method == "POST":
        form = CreateBikeForm(request.POST or None)
        
        if form.is_valid():
            fab_year = form.cleaned_data.get("fab_year")
            
            new_bike = Bike(    category = Category.objects.get(category = form.cleaned_data.get("category")), 
                                company = form.cleaned_data.get("company"), 
                                model = form.cleaned_data.get("model"), 
                                fab_year = fab_year, 
                                bike_img = form.cleaned_data.get("bike_img"),
                                description = form.cleaned_data.get("description"), 
                                posted_by = request.user)

            open_bid = Bid(     bid = form.cleaned_data.get("first_bid"), 
                                bike = new_bike, 
                                user = request.user)

            try:
                new_bike.clean_fab_year(fab_year)
                new_bike.save()
                open_bid.save()
                messages.success(request, "Bike added successfully")
                return redirect(reverse("index"))
                
            except ValidationError:
                messages.error(request, "Invalid fabrication year")
                content = general_reducer("create")
                return redirect(reverse("createbike"), content)

        else:
            messages.error(request, "Invalid form data")
            content = general_reducer("create")
            return redirect(reverse("createbike"), content)
    
    elif request.method == "GET":
        content = general_reducer("create")
        return render(request, "auctions/createbike.html", content)


@login_required(login_url = "login")
def watchlist(request):
    user = request.user
    
    if request.method == "POST":
        if "bike_id" in request.POST:
            bike_id = request.POST.get("bike_id")
            bike = Bike.objects.get(bike_id = bike_id)
                                    
            if WatchList.objects.filter(bike = bike, user = user).exists():
                messages.info(request, "Bike already on watchlist")
                return redirect(reverse("watchlist"))
                
            else:
                WatchList(bike = bike, user = user).save()
                messages.info(request, "Bike added to watchlist")
                return redirect(reverse("watchlist"))
                
    elif request.method == "GET":
        watchlist = user.watchlist_by_user.all()
        if not watchlist:
            messages.info(request, "Watchlist Empty")
        content = {"watchlist": watchlist}
        return render(request, "auctions/watchlist.html", content)
    
    return redirect(reverse("index"))


@login_required(login_url = "login")
def removelist(request, watch_id):
    if request.method == "GET":
        WatchList.objects.get(watch_id = watch_id).delete()
    return redirect(reverse("watchlist"))


@login_required(login_url = "login")
def deactivate(request, bike_id):
    if request.method == "POST":
        print("IN DEACTIVATE")
        bike = Bike.objects.get(bike_id = bike_id)
        bike.watchlist_by_bike.all().delete()
        bike.comment_by_bike.all().delete()
        bike.is_active = False
        bike.save()
        return redirect(reverse("index"))
    
    return redirect(reverse("index"))

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("edituser", views.edituser, name = "edituser"),
    path("change", views.changepwd, name = "change"),
    path("category", views.category, name = "category"),
    path("bikeview/<int:bike_id>", views.bikeview, name = "bikeview"),
    path("createbike", views.createbike, name = "createbike"),
    path("watchlist", views.watchlist, name = "watchlist"),
    path("remove/<int:watch_id>", views.removelist, name = "removelist"),
    path("deactivate/<int:bike_id>", views.deactivate, name = "deactivate")
]

"""
    path("addtowatchlist/<int:bike_id>", views.addtowatchlist, name = "addtowatchlist"),
    path("removewatchlist/<int:watch_id>", views.removewatchlist, name = "removewatchlist")
    """
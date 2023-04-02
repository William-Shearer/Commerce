from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Category


class LoginForm(forms.Form):
    username = forms.CharField(label = "User Name", max_length = 50, required = True, widget = forms.TextInput(attrs = {"autofocus": "autofocus"}))
    password = forms.CharField(label = "Password", required = True, widget = forms.PasswordInput())

    
class RegisterForm(forms.Form):
    username = forms.CharField(label = "User Name", max_length = 50, required = True, widget = forms.TextInput(attrs = {"autofocus":"autofocus"}))
    first_name = forms.CharField(label = "First Name", max_length = 50, required = True)
    last_name = forms.CharField(label = "Last Name", max_length = 50, required = True)
    email = forms.CharField(label = "e-mail", required = True, widget = forms.EmailInput())
    password = forms.CharField(label = "Password", required = True, widget = forms.PasswordInput())
    confirmation = forms.CharField(label = "Confirmation", required = True, widget = forms.PasswordInput())
    

class EditUserForm(forms.Form):
    first_name = forms.CharField(label = "First Name", max_length = 50, required = True, widget = forms.TextInput(attrs = {"autofocus":"autofocus"}))
    last_name = forms.CharField(label = "Last Name", max_length = 50, required = True)
    email = forms.CharField(label = "e-mail", required = True, widget = forms.EmailInput())
    
    
class ChangePasswordForm(forms.Form):
    password = forms.CharField(label = "Password", required = True, widget = forms.PasswordInput(attrs = {"autofocus":"autofocus"}))
    confirmation = forms.CharField(label = "Confirmation", required = True, widget = forms.PasswordInput())
    

class CommentForm(forms.Form):
    comment = forms.CharField(  label = "Comment", 
                                required = True,
                                max_length = 1000,
                                widget = forms.Textarea(attrs = {   "cols": 150, 
                                                                    "rows": 4, 
                                                                    "style": "resize: none; max-width: 100%; width: 100%;"}))

    
class BidForm(forms.Form):
    bid = forms.DecimalField(label = "Make a bid", required = True, max_digits = 9, decimal_places = 2)
    
    class Meta:
        localized_fields = ["__all__"]
  
class CreateBikeForm(forms.Form):
    category = forms.ModelChoiceField(label = "Category", required = True, queryset = Category.objects.all())
    company = forms.CharField(label="Manufacture Company", required = True, max_length = 50)
    model = forms.CharField(label = "Bike Model", required = True, max_length = 50)
    fab_year = forms.IntegerField(label = "Fabrication Year", required = True, localize = False)
    description = forms.CharField(label = "Description", required = False, widget = forms.Textarea(attrs = {"rows": 4, "cols": 120}))
    bike_img = forms.URLField(label = "Image URL", required = False)
    first_bid = forms.DecimalField( label = "Opening Bid", 
                                    required = True, 
                                    max_digits = 9, 
                                    decimal_places = 2, 
                                    validators = [MinValueValidator(0.01), MaxValueValidator(9999999.99)])


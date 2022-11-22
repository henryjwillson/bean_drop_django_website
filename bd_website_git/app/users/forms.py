from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegistraterForm(UserCreationForm):  # Inheriting from django usercreationForm
    email = forms.EmailField()

    class Meta:  # 'Meta' provides nested namespace for our configurations
        model = User        # Will save to our 'User' model
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:  # 'Meta' provides nested namespace for our configurations
        model = User        # Will save to our 'User' model
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image']


class LinkCustomerReceiptsForm(forms.Form):
    customer_qr_code = forms.CharField(initial="")
    customer_secret_code = forms.CharField(initial="")

    class Meta:
        model = "users_db"
        fields = ['QR_generator', 'POS_generator']

from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import ShippingDetails
class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        )]
    )
    email = forms.EmailField(
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            message='Enter a valid email address.'
        )]
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and include both letters and numbers.'
        )]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and include both letters and numbers.'
        )]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
class ShippingDetailsForm(forms.ModelForm):
    city = forms.CharField(
        max_length=100,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z\s]+$',
            message='City name can only contain letters and spaces.'
        )]
    )
    address = forms.CharField(
        max_length=255,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9\s,.-]+$',
            message='Address can only contain letters, numbers, spaces, commas, periods, and hyphens.'
        )]
    )
    postal_code = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9\s-]+$',
            message='Postal code can only contain letters, numbers, spaces, and hyphens.'
        )]
    )

    class Meta:
        model = ShippingDetails
        fields = ['city', 'address', 'postal_code']
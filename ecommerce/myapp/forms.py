from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from .models import Profile

# Custom User Creation Form
class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., john_doe123'})
    )
    email = forms.EmailField(
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            message='Enter a valid email address in the format: example@domain.com'
        )],
        widget=forms.EmailInput(attrs={'placeholder': 'e.g., example@domain.com'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'At least 8 characters with letters and numbers'}),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and include both letters and numbers.'
        )]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and include both letters and numbers.'
        )]
    )

# Meta class for the form
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# 
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# 
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., john_doe123'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and include both letters and numbers.'
        )]
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    
    # 
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'postal_code', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}),
            'address': forms.TextInput(attrs={'placeholder': 'e.g., 123 Main St, Apt 4B'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g., New York'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'e.g., 10001 or A1B 2C3'}),
        }

# Checkout Form with validation for address, city, postal code, and phone number fields using RegexValidator 
class CheckoutForm(forms.Form):
    address = forms.CharField(
        max_length=255,
        validators=[RegexValidator(
            r'^[a-zA-Z0-9\s,.-]+$',
            'Enter a valid address. For example: 123 Main St, Apt 4B.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 123 Main St, Apt 4B'}),
        help_text='Enter your complete address including apartment number if applicable.',
        error_messages={
            'required': 'Address is required.',
            'max_length': 'Address cannot exceed 255 characters.',
        }
    )
    
    city = forms.CharField(
        max_length=100,
        validators=[RegexValidator(
            r'^[a-zA-Z\s]+$',
            'Enter a valid city name. For example: New York.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., New York'}),
        error_messages={
            'required': 'City is required.',
            'max_length': 'City name cannot exceed 100 characters.',
        }
    )
    
    postal_code = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            r'^\d{5}(-\d{4})?$|^[A-Z]\d[A-Z] \d[A-Z]\d$',
            'Enter a valid postal code. For example: 10001 or A1B 2C3.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 10001 or A1B 2C3'}),
        error_messages={
            'required': 'Postal code is required.',
            'max_length': 'Postal code cannot exceed 20 characters.',
        }
    )
    
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(
            r'^\+?\d{10,15}$',
            'Enter a valid phone number. For example: +1234567890.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}),
        error_messages={
            'required': 'Phone number is required.',
            'max_length': 'Phone number cannot exceed 15 characters.',
        }
    )
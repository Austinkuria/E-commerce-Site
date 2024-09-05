from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from .models import Profile

# Custom User Creation Form: Used to register new users with validation
class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., john_doe123'})  # Placeholder text for username input
    )
    email = forms.EmailField(
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
            message='Enter a valid email address in the format: example@domain.com'
        )],
        widget=forms.EmailInput(attrs={'placeholder': 'e.g., example@domain.com'})  # Placeholder text for email input
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'At least 8 characters with letters and numbers'}),  # Placeholder text for password input
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and include both letters and numbers.'
        )]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),  # Placeholder text for password confirmation
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
            message='Password must be at least 8 characters long and include both letters and numbers.'
        )]
    )

    class Meta:
        model = User  # The form is based on the User model
        fields = ['username', 'email', 'password1', 'password2']  # Fields included in the form

    def clean_password2(self):
        """Ensure that the two password fields match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")  # Error message if passwords do not match
        return password2

    def save(self, commit=True):
        """Create a new user with the provided password."""
        user = super().save(commit=False)  # Create a User instance but do not save to the database yet
        user.set_password(self.cleaned_data["password1"])  # Set the user's password
        if commit:
            user.save()  # Save the user to the database if commit is True
        return user

# Custom Login Form: Used for user authentication with validation
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., john_doe123'})  # Placeholder text for username input
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),  # Placeholder text for password input
        # validators=[RegexValidator(
        #     regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
        #     message='Password must be at least 8 characters long and include both letters and numbers.'
        # )]
    )

# User Update Form: Allows users to update their username and email
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User  # The form is based on the User model
        fields = ['username', 'email']  # Fields included in the form

# Profile Update Form: Allows users to update their profile details
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile  # The form is based on the Profile model
        fields = ['phone_number', 'address', 'city', 'postal_code', 'profile_picture']  # Fields included in the form
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}),  # Placeholder text for phone number input
            'address': forms.TextInput(attrs={'placeholder': 'e.g., 123 Main St, Apt 4B'}),  # Placeholder text for address input
            'city': forms.TextInput(attrs={'placeholder': 'e.g., New York'}),  # Placeholder text for city input
            'postal_code': forms.TextInput(attrs={'placeholder': 'e.g., 10001 or A1B 2C3'}),  # Placeholder text for postal code input
        }

# Checkout Form: Collects and validates shipping and contact information during checkout
class CheckoutForm(forms.Form):
    address = forms.CharField(
        max_length=255,
        validators=[RegexValidator(
            r'^[a-zA-Z0-9\s,.-]+$',
            'Enter a valid address. For example: 123 Kimathi St, Ln 4B.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 123 Kimathi St, Ln 4B'}),  # Placeholder text for address input
        error_messages={
            'required': 'Address is required.',  # Error message if the address field is left empty
            'max_length': 'Address cannot exceed 255 characters.',  # Error message if the address is too long
        }
    )
    
    city = forms.CharField(
        max_length=100,
        validators=[RegexValidator(
            r'^[a-zA-Z\s]+$',
            'Enter a valid city name. For example: Nairobi.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Nairobi'}),  # Placeholder text for city input
        error_messages={
            'required': 'City is required.',  # Error message if the city field is left empty
            'max_length': 'City name cannot exceed 100 characters.',  # Error message if the city name is too long
        }
    )
    
    postal_code = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            r'^\d{5}(-\d{4})?$|^[A-Z]\d[A-Z] \d[A-Z]\d$',
            'Enter a valid postal code. For example: 10001 or A1B 2C3.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 10001 or A1B 2C3'}),  # Placeholder text for postal code input
        error_messages={
            'required': 'Postal code is required.',  # Error message if the postal code field is left empty
            'max_length': 'Postal code cannot exceed 20 characters.',  # Error message if the postal code is too long
        }
    )
    
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(
            r'^\+?\d{10,15}$',
            'Enter a valid phone number. For example: +1234567890.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}),  # Placeholder text for phone number input
        error_messages={
            'required': 'Phone number is required.',  # Error message if the phone number field is left empty
            'max_length': 'Phone number cannot exceed 15 characters.',  # Error message if the phone number is too long
        }
    )

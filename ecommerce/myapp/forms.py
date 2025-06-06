from django import forms  # Import Django's forms module
from django.contrib.auth.models import User  # Import the User model for user-related forms
from django.contrib.auth.forms import AuthenticationForm  # Import AuthenticationForm for login
from django.core.validators import RegexValidator, MinValueValidator  # Import RegexValidator and MinValueValidator for custom validation
from .models import Profile  # Import the Profile model for user profile-related forms

# Custom User Creation Form: This form is used to register new users with validation
class CustomUserCreationForm(forms.ModelForm):
    # Field for the username input
    username = forms.CharField(
        max_length=150,  # Username cannot exceed 150 characters
        widget=forms.TextInput(attrs={'placeholder': 'e.g., johndoe'})  # Placeholder text to guide users
    )
    # Field for the email input
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'e.g., johndoe@gmail.com'})  # Placeholder text to guide users
    )
    # Field for the first password input
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'At least 8 characters with letters and numbers'}),  # Placeholder text to guide users
    )
    # Field for the second password input (for confirmation)
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),  # Placeholder text to guide users
    )

    class Meta:
        model = User  # This form is based on the User model
        fields = ['username', 'email', 'password1', 'password2']  # Include these fields in the form

    def clean_password2(self):
        """Ensure that the two password fields match."""
        password1 = self.cleaned_data.get("password1")  # Get the first password
        password2 = self.cleaned_data.get("password2")  # Get the second password
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")  # Raise an error if passwords do not match
        return password2  # Return the valid second password

    def save(self, commit=True):
        """Create a new user with the provided password."""
        user = super().save(commit=False)  # Create a User instance without saving it to the database
        user.set_password(self.cleaned_data["password1"])  # Set the user's password
        if commit:
            user.save()  # Save the user to the database if commit is True
        return user  # Return the created user

# Custom Login Form: This form is used for user authentication with validation
class CustomLoginForm(AuthenticationForm):
    # Field for the username input
    username = forms.CharField(
        max_length=150,  # Username cannot exceed 150 characters
        widget=forms.TextInput(attrs={'placeholder': 'e.g., johndoe'})  # Placeholder text to guide users
    )
    # Field for the password input
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),  # Placeholder text to guide users
    )

# User Update Form: This form allows users to update their username and email
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        }
        help_texts = {
            'username': 'Enter a unique username.',
            'email': 'Enter your email address.',
        }
        error_messages = {
            'username': {
                'unique': "This username is already taken. Please choose another one.",
            },
            'email': {
                'invalid': "Enter a valid email address.",
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use. Please choose another.")
        return email

class ProfileUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=False,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be in the format: '+1234567890'. Up to 15 digits allowed.")],
        help_text="Enter your phone number with the country code, e.g., +123456789.",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )
    postal_code = forms.CharField(
        required=False,
        validators=[RegexValidator(regex=r'^\d{1,10}$', message="Postal code must contain between 1 and 10 digits.")],
        help_text="Enter your postal code.",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your postal code'})
    )
    profile_picture = forms.ImageField(
        required=True,
        help_text="Upload your profile picture. If left blank, the default picture will be used."
    )

    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'postal_code', 'profile_picture']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Enter your address'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter your city'}),
        }
        help_texts = {
            'phone_number': 'Enter your phone number in international format.',
            'address': 'Enter your full address.',
            'city': 'Enter your city of residence.',
            'postal_code': 'Enter your postal code.',
            'profile_picture': 'Upload your profile picture.',
        }
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        # If 'clear' checkbox is checked, set profile_picture to None
        if self.cleaned_data.get('profile_picture_clear'):
            return None
        return profile_picture

# Base Address Form: This form is used for basic address input
class BaseAddressForm(forms.Form):
    # Field for the address input
    address = forms.CharField(
        max_length=255,  # Address cannot exceed 255 characters
        validators=[RegexValidator(
            r'^[a-zA-Z0-9\s,.-]+$',  # Address must match this regex pattern
            'Enter a valid address. For example: 123 Kimathi St, Ln 4B.'  # Error message for invalid address
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 123 Kimathi St, Ln 4B'}),  # Placeholder text to guide users
        error_messages={
            'required': 'Please provide your address.',  # Error message if address field is empty
            'max_length': 'Address cannot be longer than 255 characters.',  # Error message if address is too long
        }
    )
    
    # Field for the city input
    city = forms.CharField(
        max_length=100,  # City name cannot exceed 100 characters
        validators=[RegexValidator(
            r'^[a-zA-Z\s]+$',  # City name must match this regex pattern
            'Enter a valid city name. City name must contain only letters and spaces. For example: Nairobi.'  # Error message for invalid city name
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Nairobi'}),  # Placeholder text to guide users
        error_messages={
            'required': 'Please provide your city.',  # Error message if city field is empty
            'max_length': 'City name cannot be longer than 100 characters.',  # Error message if city name is too long
        }
    )
    
    # Field for the postal code input
    postal_code = forms.CharField(
        max_length=20,  # Postal code cannot exceed 20 characters
        validators=[RegexValidator(
            r'^\d{1,10}$',  # Postal code must match this regex pattern
            'Postal code must contain between 1 and 10 digits. For example: 12345.'  # Error message for invalid postal code
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 12345'}),  # Placeholder text to guide users
        error_messages={
            'required': 'Please provide your postal code.',  # Error message if postal code field is empty
            'max_length': 'Postal code cannot be longer than 10 digits.',  # Error message if postal code is too long
        }
    )

# Checkout Form: Extends BaseAddressForm to include additional fields for checkout
class CheckoutForm(BaseAddressForm):
    # Field for the phone number input
    phone_number = forms.CharField(
        max_length=15,  # Phone number cannot exceed 15 characters
        validators=[RegexValidator(
            r'^\+?\d{10,15}$',  # Phone number must match this regex pattern
            'Phone number must be in the format: "+1234567890". Include country code and ensure it is between 10 and 15 digits.'  # Error message for invalid phone number
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}),  # Placeholder text to guide users
        error_messages={
            'required': 'Please provide your phone number.',  # Error message if phone number field is empty
            'max_length': 'Phone number cannot be longer than 15 characters.',  # Error message if phone number is too long
        }
    )
    
    # Field for selecting a payment method
    payment_method = forms.ChoiceField(
        choices=[('visa', 'Visa'), ('mastercard', 'MasterCard'), ('mpesa', 'M-Pesa')],  # Choices for payment methods
        widget=forms.RadioSelect,  # Use radio buttons for selection
        error_messages={
            'required': 'Please select a payment method.',  # Error message if payment method is not selected
        }
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        error_messages={
            'min_value': 'Quantity must be at least 1.',
            'invalid': 'Enter a valid quantity.'
        }
    )

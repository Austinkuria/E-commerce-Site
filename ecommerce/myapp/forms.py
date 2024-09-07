from django import forms  # Import Django's forms module
from django.contrib.auth.models import User  # Import the User model for user-related forms
from django.contrib.auth.forms import AuthenticationForm  # Import AuthenticationForm for login
from django.core.validators import RegexValidator  # Import RegexValidator for custom validation
from .models import Profile  # Import the Profile model for user profile-related forms

# Custom User Creation Form: This form is used to register new users with validation
class CustomUserCreationForm(forms.ModelForm):
    # Field for the username input
    username = forms.CharField(
        max_length=150,  # Username cannot exceed 150 characters
        # validators=[RegexValidator(
        #     regex=r'^[\w.@+-]+$',  # Username must match this regex pattern
        #     message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        # )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., john_doe123'})  # Placeholder text to guide users
    )
    # Field for the email input
    email = forms.EmailField(
        # validators=[RegexValidator(
        #     regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',  # Email must match this regex pattern
        #     message='Enter a valid email address in the format: example@domain.com'
        # )],
        widget=forms.EmailInput(attrs={'placeholder': 'e.g., example@domain.com'})  # Placeholder text to guide users
    )
    # Field for the first password input
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'At least 8 characters with letters and numbers'}),  # Placeholder text to guide users
        # validators=[RegexValidator(
        #     regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',  # Password must match this regex pattern
        #     message='Password must be at least 8 characters long and include both letters and numbers.'
        # )]
    )
    # Field for the second password input (for confirmation)
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),  # Placeholder text to guide users
        # validators=[RegexValidator(
        #     regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',  # Password must match this regex pattern
        #     message='Password must be at least 8 characters long and include both letters and numbers.'
        # )]
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
        # validators=[RegexValidator(
        #     regex=r'^[\w.@+-]+$',  # Username must match this regex pattern
        #     message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        # )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., john_doe123'})  # Placeholder text to guide users
    )
    # Field for the password input
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),  # Placeholder text to guide users
        # validators=[RegexValidator(
        #     regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',  # Password must match this regex pattern
        #     message='Password must be at least 8 characters long and include both letters and numbers.'
        # )]
    )

# User Update Form: This form allows users to update their username and email
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User  # This form is based on the User model
        fields = ['username', 'email']  # Include these fields in the form
        help_texts = {
            'username': 'Enter a unique username.',  # Help text for the username field
            'email': 'Enter your email address.',  # Help text for the email field
        }
        error_messages = {
            'username': {
                'unique': "This username is already taken. Please choose another one.",  # Error message if username is not unique
            },
            'email': {
                'invalid': "Enter a valid email address.",  # Error message if email is invalid
            },
        }

    def clean_email(self):
        """Ensure that the email is unique."""
        email = self.cleaned_data.get('email')  # Get the email from cleaned data
        # Check if the email is already in use by another user (excluding the current user)
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use. Please choose another.")  # Raise an error if email is not unique
        return email  # Return the valid email

# Profile Update Form: This form allows users to update their profile information
class ProfileUpdateForm(forms.ModelForm):
    # Field for the phone number input
    phone_number = forms.CharField(
        required=False,  # This field is optional
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed.")],  # Validate phone number format
        help_text="Enter your phone number with the country code, e.g., +123456789."  # Help text for the phone number field
    )
    # Field for the postal code input
    postal_code = forms.CharField(
        required=False,  # This field is optional
        validators=[RegexValidator(regex=r'^\d{4,10}$', message="Postal code must contain between 4 and 10 digits.")],  # Validate postal code format
        help_text="Enter your postal code."  # Help text for the postal code field
    )
    # Field for the profile picture upload
    profile_picture = forms.ImageField(
        required=False,  # This field is optional
        help_text="Upload your profile picture. If left blank, the default picture will be used."  # Help text for the profile picture field
    )

    class Meta:
        model = Profile  # This form is based on the Profile model
        fields = ['phone_number', 'address', 'city', 'postal_code', 'profile_picture']  # Include these fields in the form
        help_texts = {
            'phone_number': 'Enter your phone number in international format.',  # Help text for the phone number field
            'address': 'Enter your full address.',  # Help text for the address field
            'city': 'Enter your city of residence.',  # Help text for the city field
            'postal_code': 'Enter your postal code.',  # Help text for the postal code field
            'profile_picture': 'Upload your profile picture.',  # Help text for the profile picture field
        }
        error_messages = {
            'phone_number': {
                'invalid': "Phone number must be in the format '+999999999'.",  # Error message for invalid phone number
            },
            'postal_code': {
                'invalid': "Postal code must be numeric and between 4 and 10 digits.",  # Error message for invalid postal code
            },
        }

    def clean_phone_number(self):
        """Ensure the phone number starts with a '+' sign."""
        phone_number = self.cleaned_data.get('phone_number')  # Get the phone number from cleaned data
        # Raise an error if the phone number does not start with '+'
        if phone_number and not phone_number.startswith('+'):
            raise forms.ValidationError("Phone number must start with a '+' sign.")
        return phone_number  # Return the valid phone number

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
            'Enter a valid city name. For example: Nairobi.'  # Error message for invalid city name
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
            r'^\d{4,10}$',  # Postal code must match this regex pattern
            'Postal code must contain between 4 and 10 digits. For example: 10001.'  # Error message for invalid postal code
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 12345'}),  # Placeholder text to guide users
        error_messages={
            'required': 'Please provide your postal code.',  # Error message if postal code field is empty
            'max_length': 'Postal code cannot be longer than 20 characters.',  # Error message if postal code is too long
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

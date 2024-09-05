from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from .models import Profile

# Custom User Creation Form: Used to register new users with validation
class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        # validators=[RegexValidator(
        #     regex=r'^[\w.@+-]+$',
        #     message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        # )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., john_doe123'})  # Placeholder text for username input
    )
    email = forms.EmailField(
        # validators=[RegexValidator(
        #     regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
        #     message='Enter a valid email address in the format: example@domain.com'
        # )],
        widget=forms.EmailInput(attrs={'placeholder': 'e.g., example@domain.com'})  # Placeholder text for email input
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'At least 8 characters with letters and numbers'}),  # Placeholder text for password input
        # validators=[RegexValidator(
        #     regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
        #     message='Password must be at least 8 characters long and include both letters and numbers.'
        # )]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter your password'}),  # Placeholder text for password confirmation
        # validators=[RegexValidator(
        #     regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
        #     message='Password must be at least 8 characters long and include both letters and numbers.'
        # )]
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
        # validators=[RegexValidator(
        #     regex=r'^[\w.@+-]+$',
        #     message='Username can only contain letters, digits, and @/./+/-/_ characters.'
        # )],
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
        model = User
        fields = ['username', 'email']
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
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed.")],
        help_text="Enter your phone number with the country code, e.g., +123456789."
    )
    postal_code = forms.CharField(
        required=False,
        validators=[RegexValidator(regex=r'^\d{4,10}$', message="Postal code must contain between 4 and 10 digits.")],
        help_text="Enter your postal code."
    )
    profile_picture = forms.ImageField(
        required=False,
        help_text="Upload your profile picture. If left blank, the default picture will be used."
    )

    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'postal_code', 'profile_picture']
        help_texts = {
            'phone_number': 'Enter your phone number in international format.',
            'address': 'Enter your full address.',
            'city': 'Enter your city of residence.',
            'postal_code': 'Enter your postal code.',
            'profile_picture': 'Upload your profile picture.',
        }
        error_messages = {
            'phone_number': {
                'invalid': "Phone number must be in the format '+999999999'.",
            },
            'postal_code': {
                'invalid': "Postal code must be numeric and between 4 and 10 digits.",
            },
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.startswith('+'):
            raise forms.ValidationError("Phone number must start with a '+' sign.")
        return phone_number
 
class BaseAddressForm(forms.Form):
    address = forms.CharField(
        max_length=255,
        validators=[RegexValidator(
            r'^[a-zA-Z0-9\s,.-]+$',
            'Enter a valid address. For example: 123 Kimathi St, Ln 4B.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 123 Kimathi St, Ln 4B'}),
        error_messages={
            'required': 'Please provide your address.',
            'max_length': 'Address cannot be longer than 255 characters.',
        }
    )
    
    city = forms.CharField(
        max_length=100,
        validators=[RegexValidator(
            r'^[a-zA-Z\s]+$',
            'Enter a valid city name. For example: Nairobi.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Nairobi'}),
        error_messages={
            'required': 'Please provide your city.',
            'max_length': 'City name cannot be longer than 100 characters.',
        }
    )
    
    postal_code = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            r'^\d{4,10}$',
            'Postal code must contain between 4 and 10 digits. For example: 10001.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 10001'}),
        error_messages={
            'required': 'Please provide your postal code.',
            'max_length': 'Postal code cannot be longer than 20 characters.',
        }
    )

class CheckoutForm(BaseAddressForm):
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(
            r'^\+?\d{10,15}$',
            'Phone number must be in the format: "+1234567890". Include country code and ensure it is between 10 and 15 digits.'
        )],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}),
        error_messages={
            'required': 'Please provide your phone number.',
            'max_length': 'Phone number cannot be longer than 15 characters.',
        }
    )
    
    # 
    payment_method = forms.ChoiceField(
        choices=[('visa', 'Visa'), ('mastercard', 'MasterCard'), ('mpesa', 'M-Pesa')],
        widget=forms.RadioSelect,
        error_messages={
            'required': 'Please select a payment method.',
        }
    )
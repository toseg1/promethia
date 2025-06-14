"""
Forms for user registration and profile management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
    
class SignUpForm(UserCreationForm):
    """Extended user registration form with comprehensive validation."""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True) 
    role = forms.ChoiceField(choices=[('', 'Select your role')] + list(Profile.ROLE_CHOICES),
                    required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ==== CRITICAL: Override ALL error messages in __init__ ====
        # This is the ONLY reliable way to override Django's built-in messages
        
        # USERNAME field (inherited from UserCreationForm)
        self.fields['username'].error_messages = {
            'required': 'Username is required.',
            'unique': 'This username is already taken.',
            'invalid': 'Username can only contain letters, numbers, and underscores.',
            'max_length': 'Username cannot be longer than 150 characters.',
        }
        
        # EMAIL field (our custom field)
        self.fields['email'].error_messages = {
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.',
            'unique': 'This email address is already taken.',
        }
        
        # FIRST NAME field (our custom field)
        self.fields['first_name'].error_messages = {
            'required': 'First name is required.',
            'max_length': 'First name cannot be longer than 30 characters.',
        }
        
        # LAST NAME field (our custom field)
        self.fields['last_name'].error_messages = {
            'required': 'Last name is required.',
            'max_length': 'Last name cannot be longer than 30 characters.',
        }
        
        # ROLE field (our custom field)
        self.fields['role'].error_messages = {
            'required': 'Please select your role (Athlete or Coach).',
            'invalid_choice': 'Please select either Athlete or Coach.',
        }
        
        # PASSWORD1 field (inherited from UserCreationForm)
        self.fields['password1'].error_messages = {
            'required': 'Password is required.',
        }
        
        # PASSWORD2 field (inherited from UserCreationForm)
        self.fields['password2'].error_messages = {
            'required': 'Please confirm your password.',
        }
        
        # Add CSS classes and styling to all fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email (e.g., user@example.com)'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'First Name'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

    def clean_username(self):
        """Custom username validation with proper error messages."""
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError('Username is required.')
        
        username = username.strip()
        
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.')
        elif len(username) > 30:
            raise ValidationError('Username cannot be longer than 30 characters.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken. Please choose a different one.')
        
        return username

    def clean_email(self):
        """Custom email validation with proper error messages."""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email address is required.')
        
        email = email.strip().lower()
        
        # Email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('Please enter a valid email address (e.g., user@example.com).')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists. Please use a different email or try logging in.')
        
        return email

    def clean_first_name(self):
        """Custom first name validation with proper error messages."""
        first_name = self.cleaned_data.get('first_name')
        
        if not first_name or not first_name.strip():
            raise ValidationError('First name is required.')
        
        first_name = first_name.strip()
        
        if len(first_name) > 30:
            raise ValidationError('First name cannot be longer than 30 characters.')
        
        return first_name

    def clean_last_name(self):
        """Custom last name validation with proper error messages."""
        last_name = self.cleaned_data.get('last_name')
        
        if not last_name or not last_name.strip():
            raise ValidationError('Last name is required.')
        
        last_name = last_name.strip()
        
        if len(last_name) > 30:
            raise ValidationError('Last name cannot be longer than 30 characters.')
        
        return last_name

    def clean_role(self):
        """Custom role validation with proper error messages."""
        role = self.cleaned_data.get('role')
        
        if not role:
            raise ValidationError('Please select your role (Athlete or Coach).')
        
        if role not in ['athlete', 'coach']:
            raise ValidationError('Please select either Athlete or Coach.')
        
        return role

    def clean_password2(self):
        """Custom password confirmation validation with proper error messages."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if not password2:
            raise ValidationError('Please confirm your password.')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('The two password fields must match.')
        
        return password2

    def save(self, commit=True):
        """Save user with all required fields."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Profile editing form with comprehensive validation."""
    
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Profile
        fields = ['phone_number', 'bio', 'profile_picture', 'date_of_birth', 'club', 
                 'role','vma', 'ftp', 'css']
        
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+33 6 12 34 56 78'
            }),
            'club': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your sports club or team'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'vma': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'km/h',
                'min': '0',
                'max': '30'
            }),
            'ftp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'watts',
                'min': '0',
                'max': '1000'
            }),
            'css': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1:45/100m',
                'pattern': r'[0-9]:[0-5][0-9]/100m'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Override ALL field error messages in __init__
        self.fields['first_name'].error_messages = {
            'required': 'First name is required.',
            'max_length': 'First name cannot be longer than 30 characters.',
        }
        
        self.fields['last_name'].error_messages = {
            'required': 'Last name is required.',
            'max_length': 'Last name cannot be longer than 30 characters.',
        }
        
        self.fields['phone_number'].error_messages = {
            'max_length': 'Phone number is too long.',
        }
        
        self.fields['bio'].error_messages = {
            'max_length': 'Bio text is too long (maximum 500 characters).',
        }
        
        self.fields['profile_picture'].error_messages = {
            'invalid': 'Please upload a valid image file.',
        }
        
        self.fields['date_of_birth'].error_messages = {
            'invalid': 'Please enter a valid date.',
        }
        
        self.fields['club'].error_messages = {
            'max_length': 'Club name is too long (maximum 100 characters).',
        }
        
        self.fields['role'].error_messages = {
            'required': 'Please select your role.',
            'invalid_choice': 'Please select a valid role.',
        }
        
        self.fields['vma'].error_messages = {
            'invalid': 'Please enter a valid VMA value.',
        }
        
        self.fields['ftp'].error_messages = {
            'invalid': 'Please enter a valid FTP value.',
        }
        
        self.fields['css'].error_messages = {
            'invalid': 'Please enter a valid CSS time (e.g., 1:45/100m).',
            'max_length': 'CSS format is too long.',
        }
        
        # Pre-populate first_name and last_name from User model
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        
        # Add CSS classes to first_name and last_name
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'First Name'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    
    def clean_phone_number(self):
        """Custom phone number validation."""
        phone_number = self.cleaned_data.get('phone_number')
        
        if phone_number:
            phone_number = phone_number.strip()
            # Basic phone number validation
            if not re.match(r'^[\+]?[0-9\s\-\(\)\.]{10,15}$', phone_number):
                raise ValidationError('Please enter a valid phone number.')
        
        return phone_number
    
    def clean_vma(self):
        """Custom VMA validation."""
        vma = self.cleaned_data.get('vma')
        
        if vma is not None:
            if vma <= 0:
                raise ValidationError('VMA value must be positive.')
            if vma > 30:
                raise ValidationError('VMA value seems too high. Please check your input.')
        
        return vma
    
    def clean_ftp(self):
        """Custom FTP validation."""
        ftp = self.cleaned_data.get('ftp')
        
        if ftp is not None:
            if ftp <= 0:
                raise ValidationError('FTP value must be positive.')
            if ftp > 1000:
                raise ValidationError('FTP value seems too high. Please check your input.')
        
        return ftp
    
    def clean_css(self):
        """Custom CSS validation."""
        css = self.cleaned_data.get('css')
        
        if css:
            css = css.strip()
            # Validate CSS format (e.g., "1:45/100m")
            if not re.match(r'^[0-9]:[0-5][0-9]/100m$', css):
                raise ValidationError('CSS must be in format "M:SS/100m" (e.g., "1:45/100m").')
        
        return css
    
    def save(self, commit=True):
        """Save profile with updated user information and metric dates."""
        profile = super().save(commit=False)
        
        if commit:
            # Update user fields
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
            
            # Update sport metric dates when values change
            from datetime import date
            today = date.today()
            
            # VMA handling
            if 'vma' in self.changed_data:
                if self.cleaned_data['vma']:
                    profile.vma_updated = today
                else:
                    profile.vma_updated = None  # Clear date if value is empty
            
            # FTP handling  
            if 'ftp' in self.changed_data:
                if self.cleaned_data['ftp']:
                    profile.ftp_updated = today
                else:
                    profile.ftp_updated = None  # Clear date if value is empty
            
            # CSS handling
            if 'css' in self.changed_data:
                if self.cleaned_data['css']:
                    profile.css_updated = today
                else:
                    profile.css_updated = None  # Clear date if value is empty
                
            profile.save()
        
        return profile
    
class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with clean validation messages.
    Extends Django's AuthenticationForm.
    """
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Override error messages for built-in fields
        self.fields['username'].error_messages = {
            'required': 'Username is required.',
            'invalid': 'Please enter a valid username.',
        }
        
        self.fields['password'].error_messages = {
            'required': 'Password is required.',
        }
        
        # Remove labels if you don't want them
        self.fields['username'].label = ''
        self.fields['password'].label = ''

    def clean_username(self):
        """Custom username validation with clean error messages."""
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError('Username is required.')
        
        username = username.strip()
        
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.')
        
        # Allow both username and email login
        if '@' in username:
            # It's an email, validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, username):
                raise ValidationError('Please enter a valid email address.')
        else:
            # It's a username, validate username format
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise ValidationError('Username can only contain letters, numbers, and underscores.')
        
        return username

    def clean_password(self):
        """Custom password validation with clean error messages."""
        password = self.cleaned_data.get('password')
        
        if not password:
            raise ValidationError('Password is required.')
        
        if len(password) < 1:  # Basic check (you can add more requirements)
            raise ValidationError('Password cannot be empty.')
        
        return password

    def clean(self):
        """
        Override the main clean method to provide custom authentication error messages.
        This is called after individual field clean methods.
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Handle email login by finding the username
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username.lower())
                    username = user_obj.username
                except User.DoesNotExist:
                    raise ValidationError('No account found with this email address.')
            
            # Authenticate the user
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            
            if self.user_cache is None:
                # Check if user exists
                try:
                    user_exists = User.objects.get(username=username)
                    # User exists but password is wrong
                    raise ValidationError('Incorrect password. Please try again.')
                except User.DoesNotExist:
                    # User doesn't exist
                    raise ValidationError('No account found with this username.')
            else:
                # Check if user is active
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Custom method to check if login is allowed.
        Override with custom error messages.
        """
        if not user.is_active:
            raise ValidationError('This account has been disabled. Please contact support.')
        
class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form with styled error messages.
    """
    
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Override error messages
        self.fields['email'].error_messages = {
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.',
        }
        
        # Remove label
        self.fields['email'].label = ''

    def clean_email(self):
        """Custom email validation with styled error messages."""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email address is required.')
        
        email = email.strip().lower()
        
        # Email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError('Please enter a valid email address.')
        
        # Check if email exists in the system
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email address. Please check your email or register for a new account.')
        
        return email


# You can also create styled versions of other forms
class CustomPasswordChangeForm(forms.Form):
    """
    Custom password change form with styled error messages.
    """
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password'
        })
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        })
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Override error messages for all fields
        self.fields['old_password'].error_messages = {
            'required': 'Current password is required.',
        }
        
        self.fields['new_password1'].error_messages = {
            'required': 'New password is required.',
        }
        
        self.fields['new_password2'].error_messages = {
            'required': 'Please confirm your new password.',
        }
        
        # Remove labels
        for field in self.fields.values():
            field.label = ''

    def clean_old_password(self):
        """Validate current password."""
        old_password = self.cleaned_data.get('old_password')
        
        if not old_password:
            raise ValidationError('Current password is required.')
        
        return old_password

    def clean_new_password1(self):
        """Validate new password."""
        new_password1 = self.cleaned_data.get('new_password1')
        
        if not new_password1:
            raise ValidationError('New password is required.')
        
        if len(new_password1) < 8:
            raise ValidationError('New password must be at least 8 characters long.')
        
        if new_password1.isdigit():
            raise ValidationError('New password cannot be entirely numeric.')
        
        return new_password1

    def clean_new_password2(self):
        """Validate password confirmation."""
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        
        if not new_password2:
            raise ValidationError('Please confirm your new password.')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('The two password fields must match.')
        
        return new_password2
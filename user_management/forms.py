"""
Forms for user registration and profile management.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    """Extended user registration form."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Profile editing form."""
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
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
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
                'placeholder': 'km/h'
            }),
            'ftp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'watts'
            }),
            'css': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1:45/100m'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
    
    def save(self, commit=True):
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
    
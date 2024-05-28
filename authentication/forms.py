from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Patient, Doctor
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email is already in use.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise ValidationError('Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, a number, and a special character.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class PatientRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    contact_number = forms.CharField(max_length=15)

    class Meta:
        model = Patient
        fields = ['date_of_birth', 'gender', 'address', 'contact_number', 'blood_type', 'allergies', 'emergency_contact_name', 'emergency_contact_number']

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if not re.match(r'^\+?1?\d{9,15}$', contact_number):
            raise ValidationError('Enter a valid international phone number.')
        return contact_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user_data = {
            'username': self.cleaned_data['username'],
            'email': self.cleaned_data['email'],
            'password': self.cleaned_data['password']
        }
        user = UserRegistrationForm(user_data).save(commit=False)
        if commit:
            user.save()
            patient = super().save(commit=False)
            patient.user = user
            patient.save()
        return patient

class DoctorRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Doctor
        fields = ['specialty', 'license_number', 'bio']

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if Doctor.objects.filter(license_number=license_number).exists():
            raise ValidationError('License number must be unique.')
        return license_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user_data = {
            'username': self.cleaned_data['username'],
            'email': self.cleaned_data['email'],
            'password': self.cleaned_data['password']
        }
        user = UserRegistrationForm(user_data).save(commit=False)
        if commit:
            user.save()
            doctor = super().save(commit=False)
            doctor.user = user
            doctor.save()
        return doctor


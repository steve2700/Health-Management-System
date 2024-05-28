# authentication/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Patient, Doctor

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['date_of_birth', 'gender', 'address', 'contact_number', 'blood_type', 'allergies', 'emergency_contact_name', 'emergency_contact_number']

class DoctorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialty', 'license_number', 'bio']


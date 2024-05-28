# authentication/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Patient, Doctor

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'date_of_birth', 'gender', 'address', 'contact_number', 'blood_type', 'allergies', 'emergency_contact_name', 'emergency_contact_number']

    def validate_date_of_birth(self, value):
        # Ensure that the date_of_birth is not in the future
        if value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_contact_number(self, value):
        # Ensure that the contact_number follows a specific format (only digits)
        if not value.isdigit():
            raise serializers.ValidationError("Contact number must contain only digits.")
        return value

    def validate_blood_type(self, value):
        # Ensure that the blood_type is one of the valid choices
        valid_blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        if value not in valid_blood_types:
            raise serializers.ValidationError("Invalid blood type.")
        return value

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'specialty', 'license_number', 'bio']

    def validate_license_number(self, value):
        # Ensure that the license_number is unique
        if Doctor.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("License number must be unique.")
        return value

    def validate_bio(self, value):
        # Ensure that the bio has a maximum length of 500 characters
        max_length = 500
        if len(value) > max_length:
            raise serializers.ValidationError(f"Bio must be at most {max_length} characters.")
        return value


# authentication/serializers.py
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator, validate_email
from .models import Patient, Doctor, Appointment, Prescription, Message, Feedback, CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all()), validate_email])
    username = serializers.CharField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'profile_picture']

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone_number']

class PatientSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    full_name = serializers.ReadOnlyField(source='user.full_name')
    emergency_contact = EmergencyContactSerializer(many=True, read_only=True)
    medical_conditions = serializers.CharField(write_only=True)  # Assuming it's a text field

    class Meta:
        model = Patient
        fields = ['id', 'user', 'full_name', 'date_of_birth', 'gender', 'address', 'contact_number', 'blood_type', 'allergies', 'emergency_contact', 'medical_conditions']

    def validate_date_of_birth(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_contact_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Contact number must contain only digits.")
        if Patient.objects.filter(contact_number=value).exists():
            raise serializers.ValidationError("Contact number must be unique.")
        return value

class DoctorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    full_name = serializers.ReadOnlyField(source='user.full_name')

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'full_name', 'specialty', 'license_number', 'bio', 'is_available', 'contact_number']

    def validate_license_number(self, value):
        if Doctor.objects.filter(license_number=value).exists():
            raise serializers.ValidationError("License number must be unique.")
        return value

class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    has_prescription = serializers.BooleanField(source='prescription', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'date', 'time', 'status', 'reason_for_visit', 'additional_notes', 'is_completed', 'has_prescription']

class PrescriptionSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'patient', 'doctor', 'medication', 'dosage', 'quantity', 'refill_instructions', 'expiration_date', 'date_prescribed', 'is_active', 'notes']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    recipient_username = serializers.ReadOnlyField(source='recipient.username')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'is_read', 'is_archived', 'sender_username', 'recipient_username']

class FeedbackSerializer(serializers.ModelSerializer):
    patient_username = serializers.ReadOnlyField(source='patient.user.username')
    doctor_username = serializers.ReadOnlyField(source='doctor.user.username')

    class Meta:
        model = Feedback
        fields = ['id', 'appointment', 'patient', 'doctor', 'rating', 'comments', 'patient_username', 'doctor_username']


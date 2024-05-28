from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from django.contrib.auth.models import Permission
from django.utils import timezone

# Custom User Model
class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True, related_name='customuser_set', related_query_name='user')
    user_permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), blank=True, related_name='customuser_set', related_query_name='user')

    def __str__(self):
        return self.username


# Specialization Model
class Specialization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Emergency Contact Model
class EmergencyContact(models.Model):
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )
    ])

    def __str__(self):
        return self.name

# Medical Condition Model
class MedicalCondition(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Allergy Model
class Allergy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Patient Model
class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    address = models.TextField()
    contact_number = models.CharField(max_length=15, validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )
    ])
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.ManyToManyField(Allergy, blank=True)
    medical_conditions = models.ManyToManyField(MedicalCondition, blank=True)
    emergency_contact = models.ForeignKey(EmergencyContact, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

# Doctor Model
class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    contact_number = models.CharField(max_length=15, validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )
    ], unique=True, default='')

    def __str__(self):
        return self.user.username

# Appointment Model
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason_for_visit = models.CharField(max_length=255)
    additional_notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    prescription = models.ForeignKey('Prescription', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.patient.user.username} - {self.doctor.user.username} - {self.date}"

# Prescription Model
class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    quantity = models.IntegerField()  # Corrected field definition
    refill_instructions = models.TextField(blank=True, null=True)
    expiration_date = models.DateField()
    date_prescribed = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.user.username} - {self.doctor.user.username} - {self.medication}"


# Message Model
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    thread = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='replies')

    def __str__(self):
        return f"{self.sender.username} - {self.recipient.username} - {self.timestamp}"

# Feedback Model
class Feedback(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.user.username} - {self.doctor.user.username} - {self.rating}"



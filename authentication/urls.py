# authentication/urls.py
from django.urls import path
from .views import patient_register, doctor_register, patient_login, doctor_login, create_prescription, list_appointments, manage_appointments

urlpatterns = [
    path('patient/register/', patient_register, name='patient_register'),
    path('doctor/register/', doctor_register, name='doctor_register'),
    path('patient/login/', patient_login, name='patient_login'),
    path('doctor/login/', doctor_login, name='doctor_login'),
    path('prescriptions/create/', create_prescription, name='create_prescription'),
    path('appointments/', list_appointments, name='list_appointments'),
    path('appointments/manage/', manage_appointments, name='manage_appointments'),
]


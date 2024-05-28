from django.urls import path
from .views import patient_register, doctor_register, patient_login, doctor_login

urlpatterns = [
    path('patient/register/', patient_register, name='patient_register'),
    path('doctor/register/', doctor_register, name='doctor_register'),
    path('patient/login/', patient_login, name='patient_login'),
    path('doctor/login/', doctor_login, name='doctor_login'),
]


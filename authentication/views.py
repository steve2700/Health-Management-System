# authentication/views.py
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import PatientRegistrationForm, DoctorRegistrationForm

@api_view(['POST'])
def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.data)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['email']
                )
                patient = form.save(commit=False)
                patient.user = user
                patient.save()
            return JsonResponse({'message': 'Patient registration successful'})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@api_view(['POST'])
def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.data)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['email']
                )
                doctor = form.save(commit=False)
                doctor.user = user
                doctor.save()
            return JsonResponse({'message': 'Doctor registration successful'})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
@api_view(['POST'])
def patient_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.groups.filter(name='Patients').exists():
            login(request, user)
            return JsonResponse({'message': 'Patient login successful'})
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid username or password'}, status=400)

@api_view(['POST'])
def doctor_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.groups.filter(name='Doctors').exists():
            login(request, user)
            return JsonResponse({'message': 'Doctor login successful'})
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid username or password'}, status=400)

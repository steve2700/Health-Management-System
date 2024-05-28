# authentication/views.py
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .forms import PatientRegistrationForm, DoctorRegistrationForm
from .permissions import IsDoctor, IsPatient
from .models import Patient, Doctor, Appointment, Prescription
from .serializers import PatientSerializer, DoctorSerializer, AppointmentSerializer, PrescriptionSerializer
from datetime import datetime

@api_view(['POST'])
def patient_register(request):
    form = PatientRegistrationForm(request.data)
    if form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            patient = Patient(user=user, **form.cleaned_data)
            patient.save()
            patient_group = Group.objects.get(name='Patients')
            user.groups.add(patient_group)
            token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key}, status=201)
    return JsonResponse({'errors': form.errors}, status=400)

@api_view(['POST'])
def doctor_register(request):
    form = DoctorRegistrationForm(request.data)
    if form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            doctor = Doctor(user=user, **form.cleaned_data)
            doctor.save()
            doctor_group = Group.objects.get(name='Doctors')
            user.groups.add(doctor_group)
            token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key}, status=201)
    return JsonResponse({'errors': form.errors}, status=400)

@api_view(['POST'])
def patient_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None and user.groups.filter(name='Patients').exists():
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key}, status=200)
    return JsonResponse({'error': 'Invalid credentials or not a patient'}, status=400)

@api_view(['POST'])
def doctor_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None and user.groups.filter(name='Doctors').exists():
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key}, status=200)
    return JsonResponse({'error': 'Invalid credentials or not a doctor'}, status=400)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsPatient])
def list_appointments(request):
    if request.method == 'GET':
        patient = request.user.patient
        appointments = Appointment.objects.filter(patient=patient)

        # Filtering
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status = request.query_params.get('status')
        if date_from:
            appointments = appointments.filter(date__gte=date_from)
        if date_to:
            appointments = appointments.filter(date__lte=date_to)
        if status:
            appointments = appointments.filter(status=status)

        # Sorting
        sort_by = request.query_params.get('sort_by', 'date')
        if sort_by in ['date', 'time']:
            appointments = appointments.order_by(sort_by)

        serializer = AppointmentSerializer(appointments, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = request.data
        doctor = Doctor.objects.get(id=data['doctor'])
        appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['time'], '%H:%M').time()

        # Check for conflicts
        if Appointment.objects.filter(doctor=doctor, date=appointment_date, time=appointment_time).exists():
            return JsonResponse({'error': 'Doctor already has an appointment at this time.'}, status=400)
        if Appointment.objects.filter(patient=request.user.patient, date=appointment_date, time=appointment_time).exists():
            return JsonResponse({'error': 'You already have an appointment at this time.'}, status=400)

        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(patient=request.user.patient)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated, IsDoctor])
def manage_appointments(request):
    if request.method == 'GET':
        doctor = request.user.doctor
        appointments = Appointment.objects.filter(doctor=doctor)

        # Filtering
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status = request.query_params.get('status')
        if date_from:
            appointments = appointments.filter(date__gte=date_from)
        if date_to:
            appointments = appointments.filter(date__lte=date_to)
        if status:
            appointments = appointments.filter(status=status)

        # Sorting
        sort_by = request.query_params.get('sort_by', 'date')
        if sort_by in ['date', 'time']:
            appointments = appointments.order_by(sort_by)

        serializer = AppointmentSerializer(appointments, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = request.data
        patient = Patient.objects.get(id=data['patient'])
        appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['time'], '%H:%M').time()

        # Check for conflicts
        if Appointment.objects.filter(doctor=request.user.doctor, date=appointment_date, time=appointment_time).exists():
            return JsonResponse({'error': 'You already have an appointment at this time.'}, status=400)
        if Appointment.objects.filter(patient=patient, date=appointment_date, time=appointment_time).exists():
            return JsonResponse({'error': 'Patient already has an appointment at this time.'}, status=400)

        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(doctor=request.user.doctor)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'PATCH':
        appointment_id = request.data.get('id')
        status = request.data.get('status')
        try:
            appointment = Appointment.objects.get(id=appointment_id, doctor=request.user.doctor)
            if status:
                appointment.status = status
                appointment.save()
                return JsonResponse({'message': 'Appointment status updated successfully'}, status=200)
            return JsonResponse({'error': 'Status is required'}, status=400)
        except Appointment.DoesNotExist:
            return JsonResponse({'error': 'Appointment not found'}, status=404)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def create_prescription(request):
    data = request.data
    patient = Patient.objects.get(id=data['patient'])

    # Check for allergies
    if any(allergy in data['medication'].lower() for allergy in patient.allergies.lower().split(',')):
        return JsonResponse({'error': 'Patient is allergic to the prescribed medication.'}, status=400)

    # Further validation logic can be added here

    serializer = PrescriptionSerializer(data=data)
    if serializer.is_valid():
        serializer.save(doctor=request.user.doctor, patient=patient)
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


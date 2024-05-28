# authentication/permissions.py
from rest_framework.permissions import BasePermission

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Doctors').exists()

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Patients').exists()


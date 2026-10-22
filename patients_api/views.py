from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Patient, Doctor, PatientDoctorMapping
from .serializers import (
    RegisterSerializer,
    PatientSerializer,
    DoctorSerializer,
    PatientDoctorMappingSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(
            created_by=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(
            created_by=self.request.user
        )


class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all().order_by("-created_at")
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor").order_by("-assigned_at")


class PatientMappingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # GET /api/mappings/<patient_id>/
        patient = get_object_or_404(
            Patient,
            pk=pk,
            created_by=request.user,
        )

        mappings = (
            PatientDoctorMapping.objects
            .filter(patient=patient)
            .select_related("patient", "doctor")
        )

        serializer = PatientDoctorMappingSerializer(
            mappings,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def delete(self, request, pk):
        # DELETE /api/mappings/<mapping_id>/
        mapping = get_object_or_404(
            PatientDoctorMapping.objects.filter(
                patient__created_by=request.user
            ),
            pk=pk,
        )

        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

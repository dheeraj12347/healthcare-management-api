
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Patient, Doctor, PatientDoctorMapping

User = get_user_model()


class HealthcareAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            name="Owner User",
            password="StrongTestPass123!",
        )

        self.other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            name="Other User",
            password="StrongTestPass456!",
        )

        self.patient = Patient.objects.create(
            created_by=self.user,
            name="Aarav Sharma",
            date_of_birth=date(2000, 5, 10),
            gender="M",
            phone="9876543210",
            address="Agra, Uttar Pradesh",
            medical_history="",
        )

        self.doctor = Doctor.objects.create(
            name="Dr. Priya Mehta",
            specialization="Cardiology",
            email="doctor@example.com",
            phone="9876543211",
            qualification="MBBS, MD",
            experience_years=8,
        )

    def authenticate_as(self, user):
        self.client.force_authenticate(user=user)

    def test_user_can_register(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "New User",
                "email": "newuser@example.com",
                "password": "StrongTestPass789!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email="newuser@example.com").exists()
        )

    def test_user_can_obtain_jwt_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "owner@example.com",
                "password": "StrongTestPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_patient_list_requires_authentication(self):
        response = self.client.get("/api/patients/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_list_own_patients(self):
        self.authenticate_as(self.user)

        response = self.client.get("/api/patients/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.patient.id)

    def test_user_cannot_access_another_users_patient(self):
        self.authenticate_as(self.other_user)

        response = self.client.get(
            f"/api/patients/{self.patient.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_future_date_of_birth_is_rejected(self):
        self.authenticate_as(self.user)

        response = self.client.post(
            "/api/patients/",
            {
                "name": "Invalid Patient",
                "date_of_birth": (date.today() + timedelta(days=1)).isoformat(),
                "gender": "M",
                "phone": "9876543210",
                "address": "Test Address",
                "medical_history": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date_of_birth", response.data)

    def test_authenticated_user_can_list_doctors(self):
        self.authenticate_as(self.user)

        response = self.client.get("/api/doctors/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(item["id"] == self.doctor.id for item in response.data)
        )

    def test_user_can_create_patient_doctor_mapping(self):
        self.authenticate_as(self.user)

        response = self.client.post(
            "/api/mappings/",
            {
                "patient": self.patient.id,
                "doctor": self.doctor.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            PatientDoctorMapping.objects.filter(
                patient=self.patient,
                doctor=self.doctor,
            ).exists()
        )

    def test_duplicate_mapping_is_rejected(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
        )
        self.authenticate_as(self.user)

        response = self.client.post(
            "/api/mappings/",
            {
                "patient": self.patient.id,
                "doctor": self.doctor.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_list_another_users_patient_mappings(self):
        self.authenticate_as(self.other_user)

        response = self.client.get(
            f"/api/mappings/{self.patient.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_patient_create_retrieve_update_delete(self):
        self.authenticate_as(self.user)

        response = self.client.post(
            "/api/patients/",
            {
                "name": "Test Patient",
                "date_of_birth": "1998-04-12",
                "gender": "F",
                "phone": "9876500000",
                "address": "Delhi",
                "medical_history": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        patient_id = response.data["id"]

        response = self.client.get(f"/api/patients/{patient_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            f"/api/patients/{patient_id}/",
            {
                "name": "Updated Patient",
                "date_of_birth": "1998-04-12",
                "gender": "F",
                "phone": "9876500001",
                "address": "Delhi",
                "medical_history": "Updated history",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Patient")

        response = self.client.delete(f"/api/patients/{patient_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_doctor_create_retrieve_update_delete(self):
        self.authenticate_as(self.user)

        response = self.client.post(
            "/api/doctors/",
            {
                "name": "Dr. Test",
                "specialization": "Neurology",
                "email": "newdoctor@example.com",
                "phone": "9876500002",
                "qualification": "MBBS",
                "experience_years": 5,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doctor_id = response.data["id"]

        response = self.client.get(f"/api/doctors/{doctor_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            f"/api/doctors/{doctor_id}/",
            {
                "name": "Dr. Test Updated",
                "specialization": "Neurology",
                "email": "newdoctor@example.com",
                "phone": "9876500003",
                "qualification": "MBBS, MD",
                "experience_years": 6,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Dr. Test Updated")

        response = self.client.delete(f"/api/doctors/{doctor_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_list_mappings(self):
        self.authenticate_as(self.user)
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
        )

        response = self.client.get("/api/mappings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_can_retrieve_patient_mappings(self):
        self.authenticate_as(self.user)
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
        )

        response = self.client.get(f"/api/mappings/{self.patient.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["doctor"], self.doctor.id)

    def test_user_can_delete_mapping(self):
        self.authenticate_as(self.user)
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
        )

        response = self.client.delete(f"/api/mappings/{mapping.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            PatientDoctorMapping.objects.filter(pk=mapping.id).exists()
        )

    def test_user_cannot_assign_doctor_to_another_users_patient(self):
        self.authenticate_as(self.other_user)

        response = self.client.post(
            "/api/mappings/",
            {
                "patient": self.patient.id,
                "doctor": self.doctor.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_jwt_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "owner@example.com",
                "password": "StrongTestPass123!",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": login_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

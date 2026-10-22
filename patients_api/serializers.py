
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Patient, Doctor, PatientDoctorMapping

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "name", "email", "password"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data["email"]

        user = User(
            username=email,
            **validated_data,
        )
        user.set_password(password)
        user.save()
        return user


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "date_of_birth",
            "gender",
            "phone",
            "address",
            "medical_history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_date_of_birth(self, value):
        from datetime import date

        if value > date.today():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )
        return value


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialization",
            "email",
            "phone",
            "qualification",
            "experience_years",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_email(self, value):
        value = value.strip().lower()
        queryset = Doctor.objects.filter(email__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A doctor with this email already exists."
            )
        return value


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all()
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor", "assigned_at"]
        read_only_fields = ["id", "assigned_at"]

    def validate_patient(self, patient):
        request = self.context.get("request")

        if request and patient.created_by_id != request.user.id:
            raise serializers.ValidationError(
                "You can only assign doctors to your own patients."
            )

        return patient

    def validate(self, attrs):
        patient = attrs.get(
            "patient",
            getattr(self.instance, "patient", None),
        )
        doctor = attrs.get(
            "doctor",
            getattr(self.instance, "doctor", None),
        )

        if patient and doctor:
            mappings = PatientDoctorMapping.objects.filter(
                patient=patient,
                doctor=doctor,
            )

            if self.instance:
                mappings = mappings.exclude(pk=self.instance.pk)

            if mappings.exists():
                raise serializers.ValidationError(
                    "This doctor is already assigned to this patient."
                )

        return attrs

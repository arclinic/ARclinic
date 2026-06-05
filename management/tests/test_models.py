import pytest
from management.models import Patient


@pytest.mark.django_db
class TestPatient:
    def test_full_name(self):
        patient = Patient(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
        )
        assert patient.full_name == "Иванов Иван Иванович"

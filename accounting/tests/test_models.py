import pytest
from accounting.models import Account


@pytest.mark.django_db
class TestAccount:
    def test_create_account(self):
        account = Account.objects.create(
            name="Касса",
            code="50",
            account_type="active",
        )
        assert account.code == "50"
        assert str(account) == "Касса"

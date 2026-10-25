from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import FxRate
from tests.conftest import ATTENTION_TITLE
from tests.employee_write_factories import employee_input


def test_new_below_band_employee_immediately_changes_insight_summary(
    attention_client: TestClient, session: Session,
) -> None:
    session.add(FxRate(currency="USD", usd_rate_e6=1_000_000))
    session.commit()
    before = attention_client.get("/insights/bands").json()["summary"]["below_min"]
    response = attention_client.post("/employees", json=employee_input(
        title=ATTENTION_TITLE, salary_minor=100,
    ).model_dump(mode="json"))
    assert response.status_code == 201
    after = attention_client.get("/insights/bands").json()["summary"]["below_min"]
    assert after == before + 1

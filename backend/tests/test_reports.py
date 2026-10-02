import pytest

REPORTS = [
    "/api/reports/step-costs",
    "/api/reports/team-experience",
    "/api/reports/delays",
    "/api/reports/workflow?max_nodes=50",
    "/api/reports/workflow?step=Assemblage%20r%C3%A9acteurs",
    "/api/reports/step-details?step=Assemblage%20r%C3%A9acteurs",
]


@pytest.mark.parametrize("url", REPORTS)
def test_report_renders(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "Error" not in response.get_data(as_text=True)[:200]


def test_steps_lists_mes_steps(client):
    steps = client.get("/api/steps").get_json()
    assert "Assemblage réacteurs" in steps


def test_step_details_rejects_unknown_step(client):
    assert client.get("/api/reports/step-details?step=nope").status_code == 400

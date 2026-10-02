import pytest

from app.analytics import ANALYSES


@pytest.mark.parametrize("name", list(ANALYSES))
def test_analysis_renders(client, name):
    response = client.get(f"/api/analyses/{name}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Plotly.newPlot" in html and "Key takeaways" in html


def test_unknown_analysis_is_404(client):
    assert client.get("/api/analyses/unknown").status_code == 404

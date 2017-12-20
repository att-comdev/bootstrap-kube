import falcon
from falcon import testing
import pytest

from promenade.control import health_api
from promenade import promenade


@pytest.fixture()
def client():
    return testing.TestClient(promenade.start_promenade(disable='keystone'))

def test_get_health(client):
    response = client.simulate_get('/api/v1.0/health')
    assert response.status == falcon.HTTP_204

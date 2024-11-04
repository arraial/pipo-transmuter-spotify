#!usr/bin/env python3
import pytest
from pipo_transmuter_spotify.app import get_app
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthProbes:
    @pytest.fixture
    def client(self):
        return TestClient(get_app())

    def test_livez(self, client):
        response = client.get("/livez")
        assert response.status_code == 200

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200

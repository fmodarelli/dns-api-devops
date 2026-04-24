from fastapi.testclient import TestClient
from app.main import app, zones, records

client = TestClient(app)


def setup_function():
    zones.clear()
    records.clear()


def test_create_zone():
    response = client.post("/zones", json={
        "name": "empresa.com",
        "visibility": "public",
        "description": "Zona principal"
    })
    assert response.status_code == 201
    assert response.json()["zone"]["name"] == "empresa.com"


def test_create_duplicate_zone():
    client.post("/zones", json={
        "name": "empresa.com",
        "visibility": "public",
        "description": "Zona principal"
    })

    response = client.post("/zones", json={
        "name": "empresa.com",
        "visibility": "public",
        "description": "Duplicada"
    })
    assert response.status_code == 409


def test_create_record():
    zone_response = client.post("/zones", json={
        "name": "empresa.com",
        "visibility": "public",
        "description": "Zona principal"
    })
    zone_id = zone_response.json()["zone"]["id"]

    response = client.post(f"/zones/{zone_id}/records", json={
        "name": "www",
        "record_type": "A",
        "value": "192.168.1.10"
    })
    assert response.status_code == 201
    assert response.json()["record"]["name"] == "www"


def test_create_duplicate_record_in_same_zone():
    zone_response = client.post("/zones", json={
        "name": "empresa.com",
        "visibility": "public",
        "description": "Zona principal"
    })
    zone_id = zone_response.json()["zone"]["id"]

    client.post(f"/zones/{zone_id}/records", json={
        "name": "www",
        "record_type": "A",
        "value": "192.168.1.10"
    })

    response = client.post(f"/zones/{zone_id}/records", json={
        "name": "www",
        "record_type": "CNAME",
        "value": "web.empresa.com"
    })
    assert response.status_code == 409


def test_create_record_in_nonexistent_zone():
    response = client.post("/zones/999/records", json={
        "name": "www",
        "record_type": "A",
        "value": "192.168.1.10"
    })
    assert response.status_code == 404





















































from backend.api_server import app

def test_home():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

def test_signup_page():
    client = app.test_client()
    response = client.get("/signup")
    assert response.status_code == 200
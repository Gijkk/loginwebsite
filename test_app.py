from app import app

def test_login_page():
    client = app.test_client()
    response = client.get("/")

    # decode nội dung HTML trả về
    text = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Đăng nhập" in text


def test_login_success():
    client = app.test_client()

    response = client.post("/", data={
        "username": "admin",
        "password": "123"
    }, follow_redirects=True)

    text = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Đăng nhập thành công" in text


def test_login_fail():
    client = app.test_client()

    response = client.post("/", data={
        "username": "sai",
        "password": "sai"
    })

    text = response.data.decode("utf-8")

    assert "Sai tài khoản" in text

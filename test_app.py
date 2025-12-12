from app import app

def test_login_page():
    # Tạo client giả để test
    client = app.test_client()

    # Gửi GET request đến trang chủ
    response = client.get("/")
    
    # Kiểm tra mã HTTP
    assert response.status_code == 200
    assert b"Đăng nhập" in text
def test_login_success():
    client = app.test_client()

    response = client.post("/", data={
        "username": "admin",
        "password": "123"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Đăng nhập thành công" in text


def test_login_fail():
    client = app.test_client()

    response = client.post("/", data={
        "username": "sai",
        "password": "sai"
    })

    assert b"Sai tài khoản" in text
    

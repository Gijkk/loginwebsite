from app import app
import pytest

TEST_USERNAME = "admin"
TEST_PASSWORD = "123"
ERROR_MESSAGE = "Sai tài khoản hoặc mật khẩu!"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success_redirects_to_success_and_sets_session(client):
    # TC001
    resp = client.post("/", data={"username": TEST_USERNAME, "password": TEST_PASSWORD}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/success" in resp.headers["Location"]

    # session should be set
    with client.session_transaction() as sess:
        assert sess.get("logged_in") is True

    # accessing /success should return 200
    resp2 = client.get("/success")
    assert resp2.status_code == 200

@pytest.mark.parametrize("username,password", [
    ("wronguser", TEST_PASSWORD),      # TC002
    (TEST_USERNAME, "wrongpass"),      # TC003
    ("foo", "bar"),                    # TC004
])
def test_login_invalid_credentials_shows_error(client, username, password):
    resp = client.post("/", data={"username": username, "password": password})
    # renders login.html with error -> 200 OK and contains error message
    assert resp.status_code == 200
    assert ERROR_MESSAGE.encode() in resp.data
    # no session created
    with client.session_transaction() as sess:
        assert not sess.get("logged_in")

@pytest.mark.parametrize("username,password", [
    ("", TEST_PASSWORD),               # TC005 username empty
    (TEST_USERNAME, ""),               # TC006 password empty
    ("", ""),                          # TC007 both empty
])
def test_empty_fields(client, username, password):
    resp = client.post("/", data={"username": username, "password": password})
    assert resp.status_code == 200
    assert ERROR_MESSAGE.encode() in resp.data

def test_whitespace_username_and_password(client):
    # TC008, TC009, TC010 - current app compares exact values (no trim)
    resp = client.post("/", data={"username": "   ", "password": TEST_PASSWORD})
    assert resp.status_code == 200
    assert ERROR_MESSAGE.encode() in resp.data

    resp2 = client.post("/", data={"username": " admin ", "password": TEST_PASSWORD})
    assert resp2.status_code == 200
    assert ERROR_MESSAGE.encode() in resp2.data

    resp3 = client.post("/", data={"username": TEST_USERNAME, "password": " 123 "})
    assert resp3.status_code == 200
    assert ERROR_MESSAGE.encode() in resp3.data

def test_special_characters_in_username_and_password_do_not_crash(client):
    # TC011, TC012 - app should not crash and should return a normal response
    xss_payload = "<script>alert(1)</script>"
    resp = client.post("/", data={"username": xss_payload, "password": TEST_PASSWORD})
    assert resp.status_code == 200
    assert ERROR_MESSAGE.encode() in resp.data

    special_pw = "p@$$w0rd!#"
    resp2 = client.post("/", data={"username": TEST_USERNAME, "password": special_pw})
    assert resp2.status_code == 200
    assert ERROR_MESSAGE.encode() in resp2.data

@pytest.mark.parametrize("payload", [
    "admin' OR '1'='1",           # TC013
    "anything' OR 'x'='x",        # TC014
    "%admin%",                    # TC026 wildcard-like
    "admin\r\n",                  # TC027 CRLF
    "<img src=x onerror=alert(1)>",# TC015 XSS attempt
])
def test_injection_and_malicious_payloads_are_handled_safely(client, payload):
    resp = client.post("/", data={"username": payload, "password": "whatever"})
    # Application should not bypass authentication or crash
    assert resp.status_code == 200
    assert ERROR_MESSAGE.encode() in resp.data

def test_unicode_and_emoji_username_and_long_inputs(client):
    # TC016 unicode/emoji
    resp_unicode = client.post("/", data={"username": "usér😊", "password": TEST_PASSWORD})
    assert resp_unicode.status_code == 200
    assert ERROR_MESSAGE.encode() in resp_unicode.data

    # TC017 / TC018 very long inputs (stress)
    long_user = "a" * 5000
    long_pass = "p" * 5000
    resp_long = client.post("/", data={"username": long_user, "password": TEST_PASSWORD})
    assert resp_long.status_code == 200  # should not crash
    assert ERROR_MESSAGE.encode() in resp_long.data

    resp_long_pass = client.post("/", data={"username": TEST_USERNAME, "password": long_pass})
    assert resp_long_pass.status_code == 200
    assert ERROR_MESSAGE.encode() in resp_long_pass.data

def test_case_sensitivity_behavior(client):
    # TC019 username case sensitivity: app compares exact string -> should fail
    resp = client.post("/", data={"username": "Admin", "password": TEST_PASSWORD})
    assert resp.status_code == 200
    assert ERROR_MESSAGE.encode() in resp.data

    # TC020 password case sensitivity: exact match required
    resp2 = client.post("/", data={"username": TEST_USERNAME, "password": "123"})
    assert resp2.status_code == 302  # success redirect

def test_logout_clears_session_and_protects_success_route(client):
    # TC021 login
    client.post("/", data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    with client.session_transaction() as sess:
        assert sess.get("logged_in") is True

    # logout
    resp_logout = client.get("/logout", follow_redirects=False)
    assert resp_logout.status_code == 302
    assert resp_logout.headers["Location"].endswith("/")

    # session cleared
    with client.session_transaction() as sess:
        assert not sess.get("logged_in")

    # accessing /success should redirect to login
    resp = client.get("/success", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")

def test_access_success_without_login_redirects_to_login(client):
    # TC022
    resp = client.get("/success", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")

def test_session_is_isolated_between_clients():
    # TC025
    app.config['TESTING'] = True
    client_a = app.test_client()
    client_b = app.test_client()

    # A logs in successfully
    client_a.post("/", data={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    with client_a.session_transaction() as sa:
        assert sa.get("logged_in") is True

    # B has no session / not logged in
    with client_b.session_transaction() as sb:
        assert not sb.get("logged_in")



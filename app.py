from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret-key-demo"  # cần để sử dụng session

# Fake tài khoản
USERNAME = "admin"
PASSWORD = "123"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")

        if user == USERNAME and pw == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("success"))
        else:
            return render_template("login.html", error="Sai tài khoản hoặc mật khẩu!")

    return render_template("login.html")


@app.route("/success")
def success():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("success.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
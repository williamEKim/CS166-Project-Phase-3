from flask import Flask, render_template_string, redirect, url_for, request, session
import sys

from EmbeddedSQL import *
from actions import *
from buyer import *
from seller import *

app = Flask(__name__)
app.secret_key = "ebay_gui_secret"
db = None

# Templates 

MAIN_MENU = """
<h2>eBay DB Interface - Main Menu</h2>
<a href="/login"><button>Login</button></a><br><br>
<a href="/register_buyer"><button>Register as Buyer</button></a><br><br>
<a href="/register_seller"><button>Register as Seller</button></a>
"""

LOGIN_PAGE = """
<h2>Login</h2>
<form method="POST" action="/login">
    <label>Login: <input type="text" name="login" required></label><br><br>
    <label>Password: <input type="password" name="password" required></label><br><br>
    <button type="submit">Login</button>
</form>
<br><a href="/">Back</a>
{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
"""

BUYER_MENU = """
<h2>Buyer Menu — Welcome, {{ login }}!</h2>
<a href="/browse"><button>Browse Active Auctions</button></a><br><br>
<a href="/search"><button>Search Auctions</button></a><br><br>
<a href="/logout"><button>Logout</button></a>
"""

SELLER_MENU = """
<h2>Seller Menu — Welcome, {{ login }}!</h2>
<a href="/browse"><button>Browse Active Auctions</button></a><br><br>
<a href="/logout"><button>Logout</button></a>
"""

# Routes 

@app.route("/")
def main_menu():
    return render_template_string(MAIN_MENU)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        login_input = request.form["login"].strip()
        password    = request.form["password"].strip()

        # replaces login_user(db) — same query, no input()
        query = """
            SELECT login, role
            FROM "User"
            WHERE login = %s AND password = %s;
        """
        user = db.fetch_one(query, (login_input, password))

        if user is None:
            error = "Invalid login or password."
        else:
            session["login"] = user[0].strip()
            session["role"]  = user[1].strip()
            return redirect(url_for("dashboard"))

    return render_template_string(LOGIN_PAGE, error=error)


@app.route("/dashboard")
def dashboard():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    if session["role"] == "Buyer":
        return render_template_string(BUYER_MENU, login=session["login"])
    else:
        return render_template_string(SELLER_MENU, login=session["login"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main_menu"))


@app.route("/browse")
def browse():
    if "login" not in session:
        return redirect(url_for("main_menu"))
    # TODO: add table
    return "Browse page coming soon! <a href='/dashboard'>Back</a>"


# Main Logic

def main():
    global db
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <dbname> <port> <user>", file=sys.stderr)
        return

    dbname, dbport, user = sys.argv[1], sys.argv[2], sys.argv[3]
    db = EmbeddedSQL(dbname, dbport, user, "")

    print("Open your browser: http://localhost:5000")
    app.run(debug=False, port=5000)

if __name__ == "__main__":
    main()
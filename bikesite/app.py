import sqlite3
from functools import wraps

from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from hardware import station

app = Flask(__name__)
app.secret_key = "change-this-before-real-use"  # signs the login cookie
DB = "stationapp.db"


# ---------- database (users and the bike registry) ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    with sqlite3.connect(DB) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS bikes(
            id INTEGER PRIMARY KEY, serial TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL);
        """)


init_db()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---------- accounts ----------
@app.route("/")
def home():
    return redirect(url_for("dashboard" if "user_id" in session else "login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or len(password) < 6:
            flash("Enter a username and a password with at least 6 characters.")
        else:
            try:
                db = get_db()
                db.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)",
                           (username, generate_password_hash(password)))
                db.commit()
                flash("Account created. Log in below.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username is taken. Try another.")
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        row = get_db().execute("SELECT * FROM users WHERE username = ?",
                               (request.form["username"].strip(),)).fetchone()
        if row and check_password_hash(row["password_hash"], request.form["password"]):
            session.clear()
            session["user_id"], session["username"] = row["id"], row["username"]
            return redirect(url_for("dashboard"))
        flash("Wrong username or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    if session.get("user_id") == station.user_id:
        station.disconnect()
    session.clear()
    return redirect(url_for("login"))


# ---------- bikes ----------
@app.route("/bikes/register", methods=["GET", "POST"])
@login_required
def register_bike():
    if request.method == "POST":
        serial = request.form["serial"].strip().upper()
        if not serial:
            flash("Enter the bike's serial number.")
        else:
            try:
                db = get_db()
                db.execute("INSERT INTO bikes(serial, user_id) VALUES (?, ?)",
                           (serial, session["user_id"]))
                db.commit()
                flash(f"Bike {serial} registered.")
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError:
                flash("That serial number is already registered.")
    return render_template("register_bike.html")

@app.route("/bikes/remove", methods=["POST"])
@login_required
def remove_bike():
    serial = request.form["serial"].strip().upper()
    db = get_db()
    # the user_id check means you can only remove your own bikes
    cur = db.execute("DELETE FROM bikes WHERE serial = ? AND user_id = ?",
                     (serial, session["user_id"]))
    db.commit()
    if cur.rowcount:
        if station.connected and station.user_id == session["user_id"] and station.serial == serial:
            station.disconnect()  # safety: don't leave a removed bike connected
        flash(f"Bike {serial} removed.")
    else:
        flash("Bike not found.")
    return redirect(url_for("dashboard"))

# ---------- station ----------
@app.route("/dashboard")
@login_required
def dashboard():
    bikes = get_db().execute("SELECT serial FROM bikes WHERE user_id = ?",
                             (session["user_id"],)).fetchall()
    mine = station.connected and station.user_id == session["user_id"]
    return render_template("dashboard.html", bikes=bikes, connected=mine,
                           s=station.status() if mine else None,
                           in_use=station.connected and not mine)


@app.route("/connect", methods=["POST"])
@login_required
def connect():
    serial = request.form["serial"].strip().upper()
    found = get_db().execute("SELECT 1 FROM bikes WHERE serial = ? AND user_id = ?",
                             (serial, session["user_id"])).fetchone()
    if station.connected and station.user_id != session["user_id"]:
        flash("The station is in use right now.")
    elif not found:
        flash("Bike not found in the registry. Check the number or register it first.")
    else:
        station.connect(session["user_id"], serial)  # charging stays off until you start it
    return redirect(url_for("dashboard"))


@app.route("/disconnect", methods=["POST"])
@login_required
def disconnect():
    if station.user_id == session["user_id"]:
        station.disconnect()
    return redirect(url_for("dashboard"))


@app.route("/action/<name>", methods=["POST"])
@login_required
def action(name):
    if not (station.connected and station.user_id == session["user_id"]):
        flash("Connect to the station first.")
    else:
        flash(station.do(name))
    return redirect(url_for("dashboard"))


@app.route("/api/status")
@login_required
def api_status():
    if not (station.connected and station.user_id == session["user_id"]):
        return jsonify(connected=False)
    return jsonify(connected=True, **station.status())


if __name__ == "__main__":
    # host="0.0.0.0" lets a phone on the same WiFi open the site too
    app.run(host="0.0.0.0", port=5000, debug=True)
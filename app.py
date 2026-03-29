<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import requests
import random

print("Current Directory:", os.getcwd())

app = Flask(__name__, template_folder="templates")
app.secret_key = "secret123"

# ---------------- DATABASE ---------------- #
def get_db():
    conn = sqlite3.connect("database.db", timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT,
        manager_id INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        description TEXT,
        status TEXT,
        step INTEGER,
        approvals INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return redirect("/login")

# ---------------- SIGNUP ---------------- #
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role, manager_id) VALUES (?, ?, ?, ?, ?)",
            (
                request.form["name"],
                request.form["email"],
                request.form["password"],
                "employee",
                None
            )
        )

        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("signup.html")

# ---------------- LOGIN ---------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                       (request.form["email"], request.form["password"]))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ---------------- #
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    uid = session["user_id"]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id=?", (uid,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE status='approved'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE status='pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE status='rejected'")
    rejected = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           total=total,
                           approved=approved,
                           pending=pending,
                           rejected=rejected,
                           role=session["role"])

# ---------------- SUBMIT ---------------- #
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]

        # OCR simulation
        if not description:
            description = random.choice(["Food", "Travel", "Hotel"])

        # Currency conversion
        try:
            data = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
            amount *= data["rates"]["INR"]
        except:
            pass

        # Auto approval
        if amount < 1000:
            status = "approved"
            step = 3
        else:
            status = "pending"
            step = 1

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, description, status, step) VALUES (?, ?, ?, ?, ?, ?)",
            (session["user_id"], amount, category, description, status, step)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("submit.html")

# ---------------- MY EXPENSES ---------------- #
@app.route("/my_expenses")
def my_expenses():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?", (session["user_id"],))
    data = cursor.fetchall()

    conn.close()
    return render_template("my_expenses.html", expenses=data)

# ---------------- APPROVAL ---------------- #
@app.route("/approve")
def approve():
    role = session.get("role")
    uid = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    if role == "manager":
        cursor.execute("""
        SELECT e.* FROM expenses e
        JOIN users u ON e.user_id=u.id
        WHERE u.manager_id=? AND e.step=1 AND e.status='pending'
        """, (uid,))
    elif role == "admin":
        cursor.execute("SELECT * FROM expenses WHERE step=2 AND status='pending'")
    else:
        return "Unauthorized"

    data = cursor.fetchall()
    conn.close()

    return render_template("approve.html", expenses=data)

# ---------------- APPROVE ---------------- #
@app.route("/approve_expense/<int:id>")
def approve_expense(id):
    role = session.get("role")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT step, approvals FROM expenses WHERE id=?", (id,))
    exp = cursor.fetchone()

    # CFO/Admin override
    if role == "admin":
        cursor.execute("UPDATE expenses SET status='approved', step=3 WHERE id=?", (id,))
    else:
        approvals = exp["approvals"] + 1

        # 60% rule simulation (after 2 approvals approve)
        if approvals >= 2:
            cursor.execute("UPDATE expenses SET status='approved', step=3, approvals=? WHERE id=?", (approvals, id))
        else:
            cursor.execute("UPDATE expenses SET step=2, approvals=? WHERE id=?", (approvals, id))

    conn.commit()
    conn.close()

    return redirect("/approve")

# ---------------- REJECT ---------------- #
@app.route("/reject_expense/<int:id>")
def reject_expense(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE expenses SET status='rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/approve")

# ---------------- LOGOUT ---------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
=======
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import requests
import random

print("Current Directory:", os.getcwd())

app = Flask(__name__, template_folder="templates")
app.secret_key = "secret123"

# ---------------- DATABASE ---------------- #
def get_db():
    conn = sqlite3.connect("database.db", timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT,
        manager_id INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        description TEXT,
        status TEXT,
        step INTEGER,
        approvals INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return redirect("/login")

# ---------------- SIGNUP ---------------- #
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role, manager_id) VALUES (?, ?, ?, ?, ?)",
            (
                request.form["name"],
                request.form["email"],
                request.form["password"],
                "employee",
                None
            )
        )

        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("signup.html")

# ---------------- LOGIN ---------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?",
                       (request.form["email"], request.form["password"]))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ---------------- #
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    uid = session["user_id"]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id=?", (uid,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE status='approved'")
    approved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE status='pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM expenses WHERE status='rejected'")
    rejected = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           total=total,
                           approved=approved,
                           pending=pending,
                           rejected=rejected,
                           role=session["role"])

# ---------------- SUBMIT ---------------- #
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]

        # OCR simulation
        if not description:
            description = random.choice(["Food", "Travel", "Hotel"])

        # Currency conversion
        try:
            data = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
            amount *= data["rates"]["INR"]
        except:
            pass

        # Auto approval
        if amount < 1000:
            status = "approved"
            step = 3
        else:
            status = "pending"
            step = 1

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, description, status, step) VALUES (?, ?, ?, ?, ?, ?)",
            (session["user_id"], amount, category, description, status, step)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("submit.html")

# ---------------- MY EXPENSES ---------------- #
@app.route("/my_expenses")
def my_expenses():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE user_id=?", (session["user_id"],))
    data = cursor.fetchall()

    conn.close()
    return render_template("my_expenses.html", expenses=data)

# ---------------- APPROVAL ---------------- #
@app.route("/approve")
def approve():
    role = session.get("role")
    uid = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()

    if role == "manager":
        cursor.execute("""
        SELECT e.* FROM expenses e
        JOIN users u ON e.user_id=u.id
        WHERE u.manager_id=? AND e.step=1 AND e.status='pending'
        """, (uid,))
    elif role == "admin":
        cursor.execute("SELECT * FROM expenses WHERE step=2 AND status='pending'")
    else:
        return "Unauthorized"

    data = cursor.fetchall()
    conn.close()

    return render_template("approve.html", expenses=data)

# ---------------- APPROVE ---------------- #
@app.route("/approve_expense/<int:id>")
def approve_expense(id):
    role = session.get("role")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT step, approvals FROM expenses WHERE id=?", (id,))
    exp = cursor.fetchone()

    # CFO/Admin override
    if role == "admin":
        cursor.execute("UPDATE expenses SET status='approved', step=3 WHERE id=?", (id,))
    else:
        approvals = exp["approvals"] + 1

        # 60% rule simulation (after 2 approvals approve)
        if approvals >= 2:
            cursor.execute("UPDATE expenses SET status='approved', step=3, approvals=? WHERE id=?", (approvals, id))
        else:
            cursor.execute("UPDATE expenses SET step=2, approvals=? WHERE id=?", (approvals, id))

    conn.commit()
    conn.close()

    return redirect("/approve")

# ---------------- REJECT ---------------- #
@app.route("/reject_expense/<int:id>")
def reject_expense(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE expenses SET status='rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/approve")

# ---------------- LOGOUT ---------------- #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
>>>>>>> c94a1c7 (Final Hackathon Build 🚀)
    app.run(debug=True)
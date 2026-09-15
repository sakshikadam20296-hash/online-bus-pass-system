from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


# =========================
# DATABASE AND TABLES
# =========================

def create_table():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Bus Pass table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_pass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            college TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            pass_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Admin table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Add status column if old database does not have it
    try:
        cursor.execute(
            "ALTER TABLE bus_pass ADD COLUMN status TEXT DEFAULT 'Pending'"
        )
    except sqlite3.OperationalError:
        pass

    # Default Admin
    cursor.execute(
        "SELECT * FROM admins WHERE username = ?",
        ("admin",)
    )

    admin = cursor.fetchone()

    if not admin:
        cursor.execute("""
            INSERT INTO admins (username, password)
            VALUES (?, ?)
        """, ("admin", "admin123"))

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users
            (name, email, mobile, password)
            VALUES (?, ?, ?, ?)
        """, (name, email, mobile, password))

        conn.commit()
        conn.close()

        return render_template("success.html")

    return render_template("register.html")


# =========================
# USER LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE email = ? AND password = ?
        """, (email, password))

        user = cursor.fetchone()

        conn.close()

        if user:
            return render_template("dashboard.html")

        return "Invalid Email or Password!"

    return render_template("login.html")


# =========================
# USER DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# =========================
# APPLY BUS PASS
# =========================

@app.route("/apply-pass", methods=["GET", "POST"])
def apply_pass():

    if request.method == "POST":

        student_name = request.form["student_name"]
        college = request.form["college"]
        source = request.form["source"]
        destination = request.form["destination"]
        pass_type = request.form["pass_type"]
        start_date = request.form["start_date"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bus_pass
            (
                student_name,
                college,
                source,
                destination,
                pass_type,
                start_date,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name,
            college,
            source,
            destination,
            pass_type,
            start_date,
            "Pending"
        ))

        conn.commit()
        conn.close()

        return render_template("success.html")

    return render_template("apply_pass.html")


# =========================
# MY BUS PASS
# =========================

@app.route("/my-pass")
@app.route("/my-pass")
def my_pass():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM bus_pass
        ORDER BY id DESC
    """)

    passes = cursor.fetchall()

    conn.close()

    return render_template(
        "my_pass.html",
        passes=passes
    )
# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM admins
            WHERE username = ? AND password = ?
        """, (username, password))

        admin = cursor.fetchone()

        conn.close()

        if admin:
            return redirect("/admin-dashboard")

        return "Invalid Admin Username or Password!"

    return render_template("admin_login.html")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin-dashboard")
def admin_dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total Users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Total Passes
    cursor.execute("SELECT COUNT(*) FROM bus_pass")
    total_passes = cursor.fetchone()[0]

    # Pending Passes
    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_pass
        WHERE status = 'Pending'
    """)
    pending_passes = cursor.fetchone()[0]

    # Approved Passes
    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_pass
        WHERE status = 'Approved'
    """)
    approved_passes = cursor.fetchone()[0]

    # Rejected Passes
    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_pass
        WHERE status = 'Rejected'
    """)
    rejected_passes = cursor.fetchone()[0]

    # Users
    cursor.execute("""
        SELECT id, name, email, mobile
        FROM users
        ORDER BY id DESC
    """)
    users = cursor.fetchall()

    # Bus Pass Applications
    cursor.execute("""
        SELECT *
        FROM bus_pass
        ORDER BY id DESC
    """)
    passes = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_passes=total_passes,
        pending_passes=pending_passes,
        approved_passes=approved_passes,
        rejected_passes=rejected_passes,
        users=users,
        passes=passes
    )


# =========================
# APPROVE BUS PASS
# =========================

@app.route("/approve-pass/<int:pass_id>")
def approve_pass(pass_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bus_pass
        SET status = 'Approved'
        WHERE id = ?
    """, (pass_id,))

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")


# =========================
# REJECT BUS PASS
# =========================

@app.route("/reject-pass/<int:pass_id>")
def reject_pass(pass_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bus_pass
        SET status = 'Rejected'
        WHERE id = ?
    """, (pass_id,))

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    create_table()

    app.run(debug=True)
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "online_bus_pass_secret"


# =========================
# DATABASE AND TABLES
# =========================

def create_table():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # =========================
    # USERS TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)


    # =========================
    # BUS PASS TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus_pass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            college TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            pass_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            user_id INTEGER
        )
    """)


    # =========================
    # ADMIN TABLE
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)


    # Create default admin

    cursor.execute(
        "SELECT * FROM admins WHERE username = ?",
        ("admin",)
    )

    admin = cursor.fetchone()

    if not admin:

        cursor.execute("""
            INSERT INTO admins
            (username, password)
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
        """, (
            name,
            email,
            mobile,
            password
        ))


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
            SELECT *
            FROM users
            WHERE email = ?
            AND password = ?
        """, (
            email,
            password
        ))


        user = cursor.fetchone()

        conn.close()


        if user:

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            return render_template(
                "dashboard.html"
            )


        return "Invalid Email or Password!"


    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")


    return render_template(
        "dashboard.html"
    )


# =========================
# APPLY BUS PASS
# =========================

@app.route("/apply-pass", methods=["GET", "POST"])
def apply_pass():

    if "user_id" not in session:

        return redirect("/login")


    if request.method == "POST":

        student_name = request.form["student_name"]
        college = request.form["college"]
        source = request.form["source"]
        destination = request.form["destination"]
        pass_type = request.form["pass_type"]
        start_date = request.form["start_date"]

        user_id = session["user_id"]


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
                status,
                user_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name,
            college,
            source,
            destination,
            pass_type,
            start_date,
            "Pending",
            user_id
        ))


        conn.commit()
        conn.close()


        return render_template(
            "success.html"
        )


    return render_template(
        "apply_pass.html"
    )


# =========================
# MY BUS PASS
# =========================

@app.route("/my-pass")
def my_pass():

    if "user_id" not in session:

        return redirect("/login")


    user_id = session["user_id"]


    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()


    cursor.execute("""
        SELECT *
        FROM bus_pass
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))


    pass_data = cursor.fetchone()

    conn.close()


    return render_template(
        "pass_page.html",
        pass_data=pass_data
    )


# =========================
# DELETE MY PASS
# =========================

@app.route(
    "/delete-pass/<int:pass_id>",
    methods=["POST"]
)
def delete_pass(pass_id):

    if "user_id" not in session:

        return redirect("/login")


    user_id = session["user_id"]


    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()


    cursor.execute("""
        DELETE FROM bus_pass
        WHERE id = ?
        AND user_id = ?
    """, (
        pass_id,
        user_id
    ))


    conn.commit()
    conn.close()


    return redirect("/my-pass")


# =========================
# CLEAR MY HISTORY
# =========================

@app.route(
    "/clear-history",
    methods=["POST"]
)
def clear_history():

    if "user_id" not in session:

        return redirect("/login")


    user_id = session["user_id"]


    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()


    cursor.execute("""
        DELETE FROM bus_pass
        WHERE user_id = ?
    """, (user_id,))


    conn.commit()
    conn.close()


    return redirect("/my-pass")


# =========================
# ADMIN LOGIN
# =========================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()


        cursor.execute("""
            SELECT *
            FROM admins
            WHERE username = ?
            AND password = ?
        """, (
            username,
            password
        ))


        admin = cursor.fetchone()

        conn.close()


        if admin:

            return redirect(
                "/admin-dashboard"
            )


        return "Invalid Admin Username or Password!"


    return render_template(
        "admin_login.html"
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin-dashboard")
def admin_dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()


    # Total Users

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]


    # Total Passes

    cursor.execute(
        "SELECT COUNT(*) FROM bus_pass"
    )

    total_passes = cursor.fetchone()[0]


    # Pending

    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_pass
        WHERE status = 'Pending'
    """)

    pending_passes = cursor.fetchone()[0]


    # Approved

    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_pass
        WHERE status = 'Approved'
    """)

    approved_passes = cursor.fetchone()[0]


    # Rejected

    cursor.execute("""
        SELECT COUNT(*)
        FROM bus_pass
        WHERE status = 'Rejected'
    """)

    rejected_passes = cursor.fetchone()[0]


    # Users

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            mobile
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
# DELETE USER
# =========================

@app.route(
    "/delete-user/<int:user_id>",
    methods=["POST"]
)
def delete_user(user_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()


    # Delete user's bus passes

    cursor.execute("""
        DELETE FROM bus_pass
        WHERE user_id = ?
    """, (user_id,))


    # Delete user

    cursor.execute("""
        DELETE FROM users
        WHERE id = ?
    """, (user_id,))


    conn.commit()
    conn.close()


    return redirect(
        "/admin-dashboard"
    )


# =========================
# CLEAR ALL USERS HISTORY
# =========================

@app.route(
    "/clear-users",
    methods=["POST"]
)
def clear_users():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()


    # Delete all bus passes

    cursor.execute("""
        DELETE FROM bus_pass
    """)


    # Delete all users

    cursor.execute("""
        DELETE FROM users
    """)


    # Reset Users ID

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'users'
    """)


    # Reset Bus Pass ID

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'bus_pass'
    """)


    conn.commit()
    conn.close()


    return redirect(
        "/admin-dashboard"
    )


# =========================
# APPROVE BUS PASS
# =========================

@app.route(
    "/approve-pass/<int:pass_id>"
)
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


    return redirect(
        "/admin-dashboard"
    )


# =========================
# REJECT BUS PASS
# =========================

@app.route(
    "/reject-pass/<int:pass_id>"
)
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


    return redirect(
        "/admin-dashboard"
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# CREATE DATABASE
# =========================

create_table()


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )
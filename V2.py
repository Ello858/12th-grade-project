# importing packages
import tkinter as tk
from tkinter import messagebox
import mysql.connector

# ── Database Setup ───────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # change to your MySQL username
        password="262208",        # change to your MySQL password
        database="toyshop"
    )

def setup_database():
    # Connect without specifying database first to create it if needed
    conn = mysql.connector.connect(
        host="localhost",
        user="root",        # change to your MySQL username
        password="262208"         # change to your MySQL password
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS toyshop")
    cursor.execute("USE toyshop")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        )
    """)
    # Insert admin if not already there
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
            ("admin", "admin123", True)
        )
    conn.commit()
    cursor.close()
    conn.close()

# ─── Auth Logic ───────────────────────────────────────────────
def login():
    username = username_entry.get()
    password = password_entry.get()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_admin FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            if result[0]:  # is_admin is True
                messagebox.showinfo("Login", "Welcome Admin!")
                # open_admin_interface()
            else:
                messagebox.showinfo("Login", f"Welcome {username}!")
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

def signup():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Username and password cannot be empty")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
            (username, password, False)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Signup", "Account created successfully!")

    except mysql.connector.errors.IntegrityError:
        messagebox.showerror("Error", "Username already exists")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

# ─── GUI ──────────────────────────────────────────────────────
def show_login_screen():
    tk.Label(root, text="Toy Shop", font=("Arial", 16)).pack(pady=10)
    tk.Label(root, text="Username").pack()
    global username_entry
    username_entry = tk.Entry(root)
    username_entry.pack()
    tk.Label(root, text="Password").pack()
    global password_entry
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()
    tk.Button(root, text="Login", command=login).pack(pady=5)
    tk.Button(root, text="Sign Up", command=signup).pack(pady=5)

# ─── Run ──────────────────────────────────────────────────────
setup_database()
root = tk.Tk()
root.title("Toy Shop")
root.geometry("500x500")
show_login_screen()
root.mainloop()
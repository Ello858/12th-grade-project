#---------------------------------------------
# importing packages
#---------------------------------------------

import mysql.connector as m
import tkinter as tk         # for GUI
from tkinter import messagebox       # for popups

#-------------------------------------------------
# Creating Connection & Confirmation of connection
#--------------------------------------------------

con = m.connect(host="localhost", user="root", password="262208", database="toyshop")

if con.is_connected():
    print("Connection successful")
else:
    print("Connection failed")

#----------------------------------------
# Create cursor so code can be read
#----------------------------------------

mycursor = con.cursor()

#----------------------------------------
# Setup Database
#----------------------------------------

mycursor.execute("CREATE DATABASE IF NOT EXISTS toyshop")
mycursor.execute("USE toyshop")

# Check if the users table exists and has the correct number of columns (3)
# If it doesn't exist or has wrong structure, drop and recreate it
mycursor.execute("""
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = 'toyshop' AND table_name = 'users'
""")
column_count = mycursor.fetchone()[0]

if column_count != 3:
    # Table is missing or has wrong structure — recreate it
    print("Creating users table fresh...")
    mycursor.execute("DROP TABLE IF EXISTS users")
    mycursor.execute("""
        CREATE TABLE users (
            username VARCHAR(30) NOT NULL,
            password VARCHAR(30) NOT NULL,
            is_admin VARCHAR(5) DEFAULT 'no'
        )
    """)
    # Insert admin since the table is brand new
    mycursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'admin123', 'yes')")
    con.commit()
    print("Table created and admin inserted.")
else:
    # Table already exists with correct structure — keep all data!
    print("Users table already exists, keeping all data.")
    # Only insert admin if not already there
    mycursor.execute("SELECT * FROM users WHERE username = 'admin'")
    data = mycursor.fetchone()
    if not data:
        mycursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'admin123', 'yes')")
        con.commit()

#-------------------------------------------------
# Define current_user at the top
# (without this, checkout() would crash)
#-------------------------------------------------

current_user = ""

#-----------------------------------------
# Login Logic
#-----------------------------------------

def login():
    username = username_entry.get()
    password = password_entry.get()

    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    mycursor.execute(query, (username, password))
    data = mycursor.fetchone()

    if data:
        if data[2] == 'yes':  # is_admin check
            messagebox.showinfo("Login", "Welcome Admin!")
            for widget in root.winfo_children():
                widget.destroy()
            open_admin_interface()
        else:
            messagebox.showinfo("Login", "Welcome {}!".format(username))
            for widget in root.winfo_children():
                widget.destroy()
            open_customer_interface(username)
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

#---------------------------------------------------
# Signup Logic
#---------------------------------------------------

def signup():
    username = username_entry.get()
    password = password_entry.get()

    query = "SELECT * FROM users WHERE username=%s"
    mycursor.execute(query, (username,))
    data = mycursor.fetchone()

    if data:
        messagebox.showerror("Error", "Username already exists")
    else:
        mycursor.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, 'no')", (username, password))
        con.commit()
        messagebox.showinfo("Signup", "Account created successfully!")

#------------------------------------------
# Show user logic
#------------------------------------------

def show_users():
    query = "SELECT * FROM users"
    mycursor.execute(query)
    data = mycursor.fetchall()

    if data:
        # row[0] = username, row[1] = password, row[2] = is_admin
        user_list = "\n".join([f"Username: {row[0]}" for row in data])
        messagebox.showinfo("User List", user_list)
    else:
        messagebox.showinfo("User List", "No users found.")

#--------------------------------------------------------------
# Login screen gui
#--------------------------------------------------------------

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

# --------------------------
# TOY DATA
# --------------------------
toys = {
    "Teddy Bear": 500,
    "Lego Set": 1200,
    "Toy Car": 800,
    "Barbie Doll": 1000,
    "Puzzle": 300,
    "hot wheels": 400,
    "fidget spinner": 250,
    "Jigsaw Puzzle": 350,
    "Action Figure": 600,
    "rubiks cube": 450,
    "play kitchen": 1500,
}

# --------------------------
# CART SYSTEM
# --------------------------
cart = {}   # toy_name : quantity

# --------------------------
# ADD TO CART (WITH QUANTITY POPUP)
# --------------------------
def add_to_cart(toy):

    qty_window = tk.Toplevel()
    qty_window.title("Select Quantity")
    qty_window.geometry("250x150")

    tk.Label(qty_window, text=f"Quantity for {toy}").pack(pady=10)

    qty_entry = tk.Entry(qty_window)
    qty_entry.pack()

    def confirm_qty():
        qty = qty_entry.get()

        if not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("Error", "Enter a valid positive number!")
            return

        qty = int(qty)

        if toy in cart:
            cart[toy] += qty
        else:
            cart[toy] = qty

        messagebox.showinfo("Added", f"{toy} x{qty} added to cart!")
        qty_window.destroy()

    tk.Button(qty_window, text="Add", command=confirm_qty).pack(pady=10)


# --------------------------
# OPEN CART WINDOW
# --------------------------
def open_cart_window():
    cart_window = tk.Toplevel(root)
    cart_window.title("Your Cart")
    cart_window.geometry("350x400")

    tk.Label(cart_window, text="Cart Items", font=("Arial", 16)).pack(pady=10)

    if not cart:
        tk.Label(cart_window, text="Your cart is empty!", font=("Arial", 12)).pack(pady=10)
        return

    total = 0

    for toy, qty in cart.items():
        price = toys[toy] * qty
        total += price

        tk.Label(cart_window,
                 text=f"{toy}  x {qty} = ₹{price}",
                 font=("Arial", 11)).pack(anchor="w", padx=20)

    tk.Label(cart_window,
             text=f"\nTotal Amount: ₹{total}",
             font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(cart_window,
              text="Buy Now",
              bg="yellow",
              command=lambda: checkout(cart_window)).pack(pady=5)


# --------------------------
# CHECKOUT / BUY ITEMS
# --------------------------
def checkout(window):
    if not cart:
        messagebox.showerror("Empty Cart", "Your cart is empty!")
        return

    invoice = "--------- INVOICE ---------\n\n"
    total = 0

    for toy, qty in cart.items():
        price = toys[toy] * qty
        total += price
        invoice += f"{toy} x {qty} = ₹{price}\n"

    invoice += f"\nTOTAL = ₹{total}\n\nThank you for shopping!"

    messagebox.showinfo("Invoice", invoice)

    cart.clear()
    window.destroy()

    # go back to shop page
    open_customer_interface(current_user)


# --------------------------
# CUSTOMER INTERFACE
# --------------------------
def open_customer_interface(username):
    global current_user
    current_user = username

    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=f"Welcome, {username}!", font=("Arial", 14)).pack(pady=10)
    tk.Label(root, text="Available Toys:", font=("Arial", 12)).pack()

    for toy, price in toys.items():
        frame = tk.Frame(root)
        frame.pack(pady=3)

        tk.Label(frame, text=f"{toy} - ₹{price}", width=20, anchor="w").pack(side="left")
        tk.Button(frame, text="Add to Cart", command=lambda t=toy: add_to_cart(t)).pack(side="right")

    tk.Button(root, text="View Cart", command=open_cart_window, bg="lightgreen").pack(pady=10)
    tk.Button(root, text="Logout", command=go_back_to_login, bg="lightgray").pack(pady=10)


# --------------------------
# ADMIN INTERFACE
# --------------------------
def open_admin_interface():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Admin Panel", font=("Arial", 16)).pack(pady=10)
    tk.Label(root, text="Current Toys:", font=("Arial", 12)).pack(pady=5)

    for toy, price in toys.items():
        frame = tk.Frame(root)
        frame.pack(pady=3)

        tk.Label(frame, text=f"{toy} - ₹{price}", width=25, anchor="w").pack(side="left")
        tk.Button(frame, text="Edit", command=lambda t=toy: edit_toy(t)).pack(side="left", padx=5)
        tk.Button(frame, text="Delete", command=lambda t=toy: delete_toy(t)).pack(side="left")

    tk.Button(root, text="Add New Toy", command=add_new_toy, bg="lightblue").pack(pady=10)
    tk.Button(root, text="Show users", command=show_users).pack(pady=5)
    tk.Button(root, text="Logout", command=go_back_to_login, bg="lightgray").pack(pady=5)


# --------------------------
# ADD NEW TOY
# --------------------------
def add_new_toy():
    win = tk.Toplevel(root)
    win.title("Add Toy")

    tk.Label(win, text="Toy Name:").pack()
    name_entry = tk.Entry(win)
    name_entry.pack()

    tk.Label(win, text="Price:").pack()
    price_entry = tk.Entry(win)
    price_entry.pack()

    def save_toy():
        name = name_entry.get()
        price = price_entry.get()

        if name == "" or price == "":
            messagebox.showerror("Error", "Please fill all fields!")
        else:
            toys[name] = int(price)
            messagebox.showinfo("Success", "Toy added!")
            win.destroy()
            open_admin_interface()

    tk.Button(win, text="Save", command=save_toy).pack(pady=5)


# --------------------------
# EDIT TOY
# --------------------------
def edit_toy(toy_name):
    win = tk.Toplevel(root)
    win.title("Edit Toy")

    tk.Label(win, text="Toy Name:").pack()
    name_entry = tk.Entry(win)
    name_entry.insert(0, toy_name)
    name_entry.pack()

    tk.Label(win, text="Price:").pack()
    price_entry = tk.Entry(win)
    price_entry.insert(0, toys[toy_name])
    price_entry.pack()

    def save_changes():
        new_name = name_entry.get()
        new_price = price_entry.get()

        if new_name == "" or new_price == "":
            messagebox.showerror("Error", "Please fill all fields!")
        else:
            del toys[toy_name]
            toys[new_name] = int(new_price)
            messagebox.showinfo("Success", "Toy updated!")
            win.destroy()
            open_admin_interface()

    tk.Button(win, text="Save Changes", command=save_changes).pack(pady=5)


# --------------------------
# DELETE TOY
# --------------------------
def delete_toy(toy_name):
    confirm = messagebox.askyesno("Delete", f"Delete {toy_name}?")
    if confirm:
        del toys[toy_name]
        messagebox.showinfo("Deleted", "Toy removed successfully.")
        open_admin_interface()


# --------------------------
# GO BACK TO LOGIN
# --------------------------
def go_back_to_login():
    for widget in root.winfo_children():
        widget.destroy()
    show_login_screen()

#-----------------------------------------------------
# Run
#-----------------------------------------------------

root = tk.Tk()
root.title("Toy Shop")
root.geometry("600x650")
show_login_screen()
root.mainloop()
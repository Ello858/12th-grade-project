# README

## Line-by-line Explanation

### Importing Packages

```python
#---------------------------------------------
# importing packages
#---------------------------------------------

import mysql.connector as m
import tkinter as tk
from tkinter import messagebox
```

- `import mysql.connector as m`: imports the MySQL connector library and aliases it as `m`.
- `import tkinter as tk`: imports Tkinter and aliases it as `tk` for GUI creation.
- `from tkinter import messagebox`: imports the messagebox helper for popup dialogs.

### Creating Connection

```python
#-------------------------------------------------
# Creating Connection & Confirmation of connection
#--------------------------------------------------

con = m.connect(host="localhost", user="root", password="262208", database="toyshop")

if con.is_connected():
    print("Connection successful")
else:
    print("Connection failed")
```

- `con = m.connect(...)`: opens a connection to the MySQL server on `localhost` with the root user and password.
- `if con.is_connected():`: checks whether the connection succeeded.
- `print(...)`: prints the connection status to the console.

### Create Cursor

```python
#----------------------------------------
# Create cursor so code can be read
#----------------------------------------

mycursor = con.cursor()
```

- `mycursor = con.cursor()`: creates a cursor object for executing SQL queries.

### Setup Database

```python
#----------------------------------------
# Setup Database
#----------------------------------------

mycursor.execute("CREATE DATABASE IF NOT EXISTS toyshop")
mycursor.execute("USE toyshop")
```

- `mycursor.execute("CREATE DATABASE IF NOT EXISTS toyshop")`: ensures the `toyshop` database exists.
- `mycursor.execute("USE toyshop")`: selects the `toyshop` database for this session.

```python
# Check if the users table exists and has the correct number of columns (3)
# If it doesn't exist or has wrong structure, drop and recreate it
mycursor.execute("""
    SELECT COUNT(*) FROM information_schema.columns
    WHERE table_schema = 'toyshop' AND table_name = 'users'
""")
column_count = mycursor.fetchone()[0]
```

- `mycursor.execute(...)`: checks `information_schema.columns` to count columns in the `users` table.
- `column_count = mycursor.fetchone()[0]`: retrieves the numeric count result.

```python
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
```

- `if column_count != 3:`: checks whether the `users` table exists and has exactly three columns.
- `DROP TABLE IF EXISTS users`: removes the table if it exists with the wrong structure.
- `CREATE TABLE users (...)`: creates a fresh `users` table.
- `INSERT INTO users ...`: inserts the default admin user.
- `con.commit()`: writes the changes to the database.
- In the `else` block, the code preserves existing data and inserts the admin user only if it does not already exist.

### Define current_user

```python
#-------------------------------------------------
# Define current_user at the top
# (without this, checkout() would crash)
#-------------------------------------------------

current_user = ""
```

- `current_user = ""`: defines a global variable that tracks the currently logged-in customer.

### Login Logic

```python
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
```

- `def login():`: defines the login function.
- `username_entry.get()` and `password_entry.get()`: read user input from the login form.
- `query = ...`: defines a parameterized SQL login query.
- `mycursor.execute(query, (username, password))`: executes the login query.
- `data = mycursor.fetchone()`: fetches a matching user record, if any.
- `if data:`: checks whether login succeeded.
- `data[2] == 'yes'`: checks whether the user is an admin.
- `for widget in root.winfo_children(): widget.destroy()`: clears the current GUI widgets.
- `open_admin_interface()` / `open_customer_interface(username)`: opens the appropriate screen.
- `messagebox.showerror(...)`: displays a login failure message.

### Signup Logic

```python
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
```

- `def signup():`: defines the signup function.
- It checks the database for an existing username.
- If the username is already taken, it shows an error.
- Otherwise, it inserts a new non-admin user and commits the change.

### Show Users

```python
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
```

- `def show_users():`: defines a function to display all user accounts.
- `mycursor.fetchall()`: retrieves all rows from the `users` table.
- It builds a string list of usernames and displays it.

### Login Screen GUI

```python
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
```

- `show_login_screen()`: builds the login screen.
- It creates labels and entry fields for username and password.
- `username_entry` and `password_entry` are declared global so other functions can access them.
- Login and Sign Up buttons are bound to the corresponding callback functions.

### Toy Data

```python
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
```

- `toys`: an in-memory dictionary storing toy names and their prices.

### Cart System

```python
# --------------------------
# CART SYSTEM
# --------------------------
cart = {}   # toy_name : quantity
```

- `cart = {}`: begins with an empty shopping cart dictionary.

### Add to Cart

```python
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
```

- `add_to_cart(toy)`: opens a quantity selection popup for the chosen toy.
- It validates the quantity as a positive integer.
- If valid, the quantity is added to the cart or incremented if the toy is already there.
- A confirmation dialog is shown and the popup closes.

### Open Cart Window

```python
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
```

- `open_cart_window()`: opens a window showing the cart contents.
- If the cart is empty, it displays a message and returns.
- It calculates the total cost and displays each item line.
- The `Buy Now` button begins checkout.

### Checkout

```python
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
```

- `checkout(window)`: finalizes the purchase.
- It verifies the cart is not empty.
- It builds and displays an invoice string.
- It clears the cart and closes the checkout window.
- It returns the user to the customer shopping interface.

### Customer Interface

```python
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
```

- `open_customer_interface(username)`: shows the customer shopping screen.
- It stores the logged-in username in `current_user`.
- It clears the previous GUI and builds the toy list with `Add to Cart` buttons.
- It includes buttons for viewing the cart and logging out.

### Admin Interface

```python
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
```

- `open_admin_interface()`: shows the admin panel.
- It clears the main window and lists all toys with Edit/Delete buttons.
- It includes controls for adding a toy, showing users, and logging out.

### Add New Toy

```python
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
```

- `add_new_toy()`: opens a window for entering a new toy name and price.
- It validates fields and adds the new toy to the dictionary.
- After saving, it refreshes the admin screen.

### Edit Toy

```python
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
```

- `edit_toy(toy_name)`: opens an edit form prefilled with the selected toy.
- It updates the `toys` dictionary with the new values.
- It refreshes the admin screen after saving.

### Delete Toy

```python
# --------------------------
# DELETE TOY
# --------------------------
def delete_toy(toy_name):
    confirm = messagebox.askyesno("Delete", f"Delete {toy_name}?")
    if confirm:
        del toys[toy_name]
        messagebox.showinfo("Deleted", "Toy removed successfully.")
        open_admin_interface()
```

- `delete_toy(toy_name)`: prompts the admin to confirm deletion.
- If confirmed, it removes the toy from the dictionary and refreshes the admin panel.

### Go Back to Login

```python
# --------------------------
# GO BACK TO LOGIN
# --------------------------
def go_back_to_login():
    for widget in root.winfo_children():
        widget.destroy()
    show_login_screen()
```

- `go_back_to_login()`: clears the window and returns to the login screen.

### Run

```python
#-----------------------------------------------------
# Run
#-----------------------------------------------------

root = tk.Tk()
root.title("Toy Shop")
root.geometry("600x650")
show_login_screen()
root.mainloop()
```

- `root = tk.Tk()`: creates the main application window.
- `root.title("Toy Shop")`: sets the window title.
- `root.geometry("600x650")`: sets the window size.
- `show_login_screen()`: loads the login screen.
- `root.mainloop()`: starts the Tkinter event loop.

## Notes

- The app stores user accounts in the MySQL `users` table.
- Passwords are stored as plain text in the database, so this is not secure for production.
- The toy inventory remains in memory only, so toy changes are lost after closing the app.
- The admin account is automatically inserted if missing.

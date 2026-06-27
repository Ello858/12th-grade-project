# README

## Line-by-line Explanation

### Importing Packages

```python
#---------------------------------------------
# importing packages
#---------------------------------------------

import mysql.connector as m
import tkinter as tk         # for GUI
from tkinter import messagebox       # for popups
from PIL import Image, ImageTk  # for image handling
```

- `import mysql.connector as m`: imports the MySQL connector library and aliases it as `m`.
- `import tkinter as tk`: imports Tkinter and aliases it as `tk` for GUI creation.
- `from tkinter import messagebox`: imports the messagebox helper for popup dialogs.
- `from PIL import Image, ImageTk`: imports PIL (Pillow) for image handling; `Image` opens image files, `ImageTk` converts them to Tkinter-compatible format.

### Creating Connection

```python
#-------------------------------------------------
# Creating Connection & Confirmation of connection
#--------------------------------------------------

con = m.connect(host="localhost", user="root", password="262208")

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
- `username = username_entry.get()`: retrieves the username entered by the user.
- `password = password_entry.get()`: retrieves the password entered by the user.
- `query = "SELECT * FROM users WHERE username=%s AND password=%s"`: defines a parameterized SQL query to prevent SQL injection.
- `mycursor.execute(query, (username, password))`: executes the login query with the provided username and password.
- `data = mycursor.fetchone()`: fetches a matching user record, if any.
- `if data:`: checks whether login succeeded (user exists).
- `if data[2] == 'yes':`: checks whether the user is an admin (third column is 'yes').
- `messagebox.showinfo(...)`: displays a welcome message.
- `for widget in root.winfo_children(): widget.destroy()`: clears all widgets from the main window.
- `open_admin_interface()`: opens the admin panel if user is admin.
- `open_customer_interface(username)`: opens the customer shopping interface if user is a regular customer.
- `messagebox.showerror(...)`: displays a login failure message if credentials don't match.

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
- `username = username_entry.get()`: retrieves the username entered by the user.
- `password = password_entry.get()`: retrieves the password entered by the user.
- `query = "SELECT * FROM users WHERE username=%s"`: defines a query to check if the username already exists.
- `mycursor.execute(query, (username,))`: executes the query with the provided username.
- `data = mycursor.fetchone()`: fetches the result if the username exists.
- `if data:`: checks if the username already exists.
- `messagebox.showerror(...)`: shows an error if username is taken.
- `mycursor.execute("INSERT INTO users ...")`: inserts a new user with non-admin status ('no').
- `con.commit()`: saves the new user to the database.
- `messagebox.showinfo(...)`: displays a success message.

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

- `def show_users():`: defines a function to display all user accounts (admin only).
- `query = "SELECT * FROM users"`: defines a query to fetch all users.
- `mycursor.execute(query)`: executes the query.
- `data = mycursor.fetchall()`: retrieves all rows from the `users` table as a list of tuples.
- `if data:`: checks if any users exist.
- `user_list = "\n".join([...])`: creates a string with each username on a new line.
- `messagebox.showinfo(...)`: displays the user list in a popup.
- `else:`: handles the case when no users are found.

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

- `def show_login_screen():`: defines the function that builds the login screen.
- `tk.Label(root, text="Toy Shop", font=("Arial", 16)).pack(pady=10)`: creates and displays the app title.
- `tk.Label(root, text="Username").pack()`: creates a label for the username field.
- `global username_entry`: declares `username_entry` as global so other functions can access it.
- `username_entry = tk.Entry(root)`: creates a text entry widget for username input.
- `username_entry.pack()`: displays the entry widget.
- `tk.Label(root, text="Password").pack()`: creates a label for the password field.
- `global password_entry`: declares `password_entry` as global so other functions can access it.
- `password_entry = tk.Entry(root, show="*")`: creates a text entry widget for password input; `show="*"` hides the text.
- `password_entry.pack()`: displays the password entry widget.
- `tk.Button(root, text="Login", command=login).pack(pady=5)`: creates a Login button that calls the `login()` function.
- `tk.Button(root, text="Sign Up", command=signup).pack(pady=5)`: creates a Sign Up button that calls the `signup()` function.

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

- `toys = {...}`: creates a dictionary storing toy names as keys and their prices (in rupees) as values.

### Cart System

```python
# --------------------------
# CART SYSTEM
# --------------------------
cart = {}   # toy_name : quantity
```

- `cart = {}`: initializes an empty dictionary to store the shopping cart; keys are toy names and values are quantities.

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

- `def add_to_cart(toy):`: defines the function to add a toy to the cart with a quantity selector.
- `qty_window = tk.Toplevel()`: creates a new popup window.
- `qty_window.title("Select Quantity")`: sets the popup window title.
- `qty_window.geometry("250x150")`: sets the popup window size to 250x150 pixels.
- `tk.Label(qty_window, text=f"Quantity for {toy}").pack(pady=10)`: displays a label asking for quantity.
- `qty_entry = tk.Entry(qty_window)`: creates a text entry widget for quantity input.
- `qty_entry.pack()`: displays the entry widget.
- `def confirm_qty():`: defines a nested function to process the quantity input.
- `qty = qty_entry.get()`: retrieves the quantity entered by the user as a string.
- `if not qty.isdigit() or int(qty) <= 0:`: validates that the input is a positive number.
- `messagebox.showerror(...)`: shows an error message if input is invalid.
- `qty = int(qty)`: converts the quantity string to an integer.
- `if toy in cart:`: checks if the toy already exists in the cart.
- `cart[toy] += qty`: adds the quantity to the existing toy in the cart.
- `else: cart[toy] = qty`: adds the toy to the cart if it doesn't exist.
- `messagebox.showinfo(...)`: displays a confirmation message.
- `qty_window.destroy()`: closes the popup window.
- `tk.Button(qty_window, text="Add", command=confirm_qty).pack(pady=10)`: creates an Add button that calls `confirm_qty()`.

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

- `def open_cart_window():`: defines the function to display the shopping cart.
- `cart_window = tk.Toplevel(root)`: creates a new popup window for the cart.
- `cart_window.title("Your Cart")`: sets the window title.
- `cart_window.geometry("350x400")`: sets the window size to 350x400 pixels.
- `tk.Label(cart_window, text="Cart Items", ...).pack(pady=10)`: displays the "Cart Items" header.
- `if not cart:`: checks if the cart is empty.
- `tk.Label(cart_window, text="Your cart is empty!", ...).pack(pady=10)`: displays a message if cart is empty.
- `return`: exits the function early if cart is empty.
- `total = 0`: initializes the total price to 0.
- `for toy, qty in cart.items():`: iterates through each toy and its quantity in the cart.
- `price = toys[toy] * qty`: calculates the price for this toy (unit price × quantity).
- `total += price`: adds the item price to the running total.
- `tk.Label(cart_window, text=f"{toy}  x {qty} = ₹{price}", ...).pack(...)`: displays each cart item with its total price.
- `tk.Label(cart_window, text=f"\nTotal Amount: ₹{total}", ...).pack(pady=10)`: displays the total cart amount.
- `tk.Button(cart_window, text="Buy Now", bg="yellow", command=lambda: checkout(cart_window)).pack(pady=5)`: creates a Buy Now button that calls `checkout()` and passes the cart window.

### Checkout (Payment Screen with QR Code)

```python
# --------------------------
# CHECKOUT / BUY ITEMS
# --------------------------

def checkout(window):
    if not cart:
        messagebox.showerror("Empty Cart", "Your cart is empty!")
        return

    window.destroy()

    for widget in root.winfo_children():
        widget.destroy()

    # ---- title ----
    tk.Label(root, text="Payment", font=("Arial", 16, "bold")).pack(pady=10)

    # ---- main frame to hold left and right ----
    main_frame = tk.Frame(root)
    main_frame.pack(pady=10)

    # ---- LEFT: QR Code ----
    left_frame = tk.Frame(main_frame, padx=20)
    left_frame.pack(side="left")

    tk.Label(left_frame, text="Scan to Pay", font=("Arial", 12, "bold")).pack(pady=5)

    img = Image.open("QrC.jpeg")
    img = img.resize((200, 200))
    photo = ImageTk.PhotoImage(img)
    qr_label = tk.Label(left_frame, image=photo)
    qr_label.image = photo
    qr_label.pack()

    # ---- RIGHT: Bill breakdown ----
    right_frame = tk.Frame(main_frame, padx=20, bg="#f0f0f0")
    right_frame.pack(side="left", fill="both")

    tk.Label(right_frame, text="Order Summary", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)

    total = 0
    invoice = "--------- INVOICE ---------\n\n"

    for toy, qty in cart.items():
        price = toys[toy] * qty
        total += price
        invoice += f"{toy} x {qty} = ₹{price}\n"
        tk.Label(right_frame, text=f"{toy} x{qty}  →  ₹{price}",
                 font=("Arial", 10), bg="#f0f0f0", anchor="w").pack(fill="x", pady=2)

    tax = int(total * 0.10)
    grand_total = total + tax

    invoice += f"\nProject Making Tax (10%) = ₹{tax}"
    invoice += f"\nGRAND TOTAL = ₹{grand_total}\n\nThank you for shopping! 🎉"

    tk.Label(right_frame, text="─" * 25, bg="#f0f0f0").pack()
    tk.Label(right_frame, text=f"Project Tax (10%): ₹{tax}",
             font=("Arial", 10), bg="#f0f0f0", fg="gray").pack()
    tk.Label(right_frame, text=f"Total: ₹{grand_total}",
             font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=5)

    # ---- Done button ----
    def done():
        cart.clear()
        messagebox.showinfo("Thank You!", invoice)
        open_customer_interface(current_user)

    tk.Button(root, text="✅ Done!", font=("Arial", 12),
              bg="lightgreen", command=done).pack(pady=15)
```

- `def checkout(window):`: defines the checkout function that displays a professional payment screen.
- `if not cart:`: checks if the cart is empty.
- `messagebox.showerror(...)`: shows an error if cart is empty.
- `return`: exits the function if cart is empty.
- `window.destroy()`: closes the cart window passed as parameter.
- `for widget in root.winfo_children(): widget.destroy()`: clears all widgets from the main window to prepare for the payment screen.
- `tk.Label(root, text="Payment", ...).pack(pady=10)`: displays the "Payment" title.
- `main_frame = tk.Frame(root)`: creates a main container frame to hold left and right panels.
- `main_frame.pack(pady=10)`: displays the main frame.
- `left_frame = tk.Frame(main_frame, padx=20)`: creates the left frame with padding for the QR code.
- `left_frame.pack(side="left")`: positions the left frame on the left side.
- `tk.Label(left_frame, text="Scan to Pay", ...).pack(pady=5)`: displays the "Scan to Pay" label above the QR code.
- `img = Image.open("QrC.jpeg")`: opens the QR code image file using PIL.
- `img = img.resize((200, 200))`: resizes the image to 200x200 pixels.
- `photo = ImageTk.PhotoImage(img)`: converts the PIL image to a Tkinter-compatible PhotoImage object.
- `qr_label = tk.Label(left_frame, image=photo)`: creates a label to display the QR code image.
- `qr_label.image = photo`: stores a reference to the PhotoImage to prevent garbage collection.
- `qr_label.pack()`: displays the QR code label.
- `right_frame = tk.Frame(main_frame, padx=20, bg="#f0f0f0")`: creates the right frame with a light gray background for the order summary.
- `right_frame.pack(side="left", fill="both")`: positions the right frame on the left side (next to the QR code) and fills available space.
- `tk.Label(right_frame, text="Order Summary", ...).pack(pady=5)`: displays the "Order Summary" header.
- `total = 0`: initializes the total price to 0.
- `invoice = "--------- INVOICE ---------\n\n"`: initializes the invoice string.
- `for toy, qty in cart.items():`: iterates through each toy in the cart.
- `price = toys[toy] * qty`: calculates the item price.
- `total += price`: adds the item price to the running total.
- `invoice += f"{toy} x {qty} = ₹{price}\n"`: appends the item details to the invoice string.
- `tk.Label(right_frame, text=f"{toy} x{qty}  →  ₹{price}", ...).pack(...)`: displays each cart item in the order summary.
- `tax = int(total * 0.10)`: calculates 10% tax on the subtotal.
- `grand_total = total + tax`: calculates the grand total by adding tax to the subtotal.
- `invoice += f"\nProject Making Tax (10%) = ₹{tax}"`: appends the tax information to the invoice.
- `invoice += f"\nGRAND TOTAL = ₹{grand_total}\n\nThank you for shopping! 🎉"`: appends the grand total and thank you message to the invoice.
- `tk.Label(right_frame, text="─" * 25, ...).pack()`: displays a decorative line separator.
- `tk.Label(right_frame, text=f"Project Tax (10%): ₹{tax}", ...).pack()`: displays the tax amount in gray text.
- `tk.Label(right_frame, text=f"Total: ₹{grand_total}", ...).pack(pady=5)`: displays the grand total prominently in bold.
- `def done():`: defines a nested function to finalize the purchase.
- `cart.clear()`: clears all items from the cart.
- `messagebox.showinfo("Thank You!", invoice)`: displays a thank you message with the complete invoice.
- `open_customer_interface(current_user)`: returns the customer to the shopping interface.
- `tk.Button(root, text="✅ Done!", ..., command=done).pack(pady=15)`: creates a Done button that calls `done()` and completes the checkout.

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

- `def open_customer_interface(username):`: defines the function to display the customer shopping interface.
- `global current_user`: declares `current_user` as global to modify it.
- `current_user = username`: stores the logged-in username in the global variable.
- `for widget in root.winfo_children(): widget.destroy()`: clears all previous widgets from the main window.
- `tk.Label(root, text=f"Welcome, {username}!", ...).pack(pady=10)`: displays a welcome message with the customer's username.
- `tk.Label(root, text="Available Toys:", ...).pack()`: displays the "Available Toys" header.
- `for toy, price in toys.items():`: iterates through each toy in the toys dictionary.
- `frame = tk.Frame(root)`: creates a frame to hold the toy label and button side-by-side.
- `frame.pack(pady=3)`: displays the frame with vertical padding.
- `tk.Label(frame, text=f"{toy} - ₹{price}", width=20, anchor="w").pack(side="left")`: displays the toy name and price on the left.
- `tk.Button(frame, text="Add to Cart", command=lambda t=toy: add_to_cart(t)).pack(side="right")`: creates an Add to Cart button on the right that calls `add_to_cart()` with the toy name.
- `tk.Button(root, text="View Cart", command=open_cart_window, bg="lightgreen").pack(pady=10)`: creates a View Cart button.
- `tk.Button(root, text="Logout", command=go_back_to_login, bg="lightgray").pack(pady=10)`: creates a Logout button.

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

- `def open_admin_interface():`: defines the function to display the admin control panel.
- `for widget in root.winfo_children(): widget.destroy()`: clears all widgets from the main window.
- `tk.Label(root, text="Admin Panel", ...).pack(pady=10)`: displays the "Admin Panel" title.
- `tk.Label(root, text="Current Toys:", ...).pack(pady=5)`: displays the "Current Toys" header.
- `for toy, price in toys.items():`: iterates through each toy in the toys dictionary.
- `frame = tk.Frame(root)`: creates a frame to hold the toy label and buttons.
- `frame.pack(pady=3)`: displays the frame with vertical padding.
- `tk.Label(frame, text=f"{toy} - ₹{price}", ...).pack(side="left")`: displays the toy name and price.
- `tk.Button(frame, text="Edit", command=lambda t=toy: edit_toy(t)).pack(side="left", padx=5)`: creates an Edit button that calls `edit_toy()` with the toy name.
- `tk.Button(frame, text="Delete", command=lambda t=toy: delete_toy(t)).pack(side="left")`: creates a Delete button that calls `delete_toy()` with the toy name.
- `tk.Button(root, text="Add New Toy", command=add_new_toy, bg="lightblue").pack(pady=10)`: creates an Add New Toy button.
- `tk.Button(root, text="Show users", command=show_users).pack(pady=5)`: creates a Show Users button to view all registered users.
- `tk.Button(root, text="Logout", command=go_back_to_login, bg="lightgray").pack(pady=5)`: creates a Logout button.

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

- `def add_new_toy():`: defines the function for adding a new toy (admin only).
- `win = tk.Toplevel(root)`: creates a new popup window.
- `win.title("Add Toy")`: sets the window title.
- `tk.Label(win, text="Toy Name:").pack()`: displays the "Toy Name:" label.
- `name_entry = tk.Entry(win)`: creates a text entry widget for the toy name.
- `name_entry.pack()`: displays the entry widget.
- `tk.Label(win, text="Price:").pack()`: displays the "Price:" label.
- `price_entry = tk.Entry(win)`: creates a text entry widget for the toy price.
- `price_entry.pack()`: displays the entry widget.
- `def save_toy():`: defines a nested function to save the new toy.
- `name = name_entry.get()`: retrieves the toy name entered by the user.
- `price = price_entry.get()`: retrieves the price entered by the user.
- `if name == "" or price == "":`: checks if either field is empty.
- `messagebox.showerror(...)`: shows an error message if fields are empty.
- `else:`: executes if both fields are filled.
- `toys[name] = int(price)`: adds the new toy to the dictionary with the price converted to an integer.
- `messagebox.showinfo(...)`: displays a success message.
- `win.destroy()`: closes the Add Toy popup window.
- `open_admin_interface()`: refreshes the admin panel to show the new toy.
- `tk.Button(win, text="Save", command=save_toy).pack(pady=5)`: creates a Save button that calls `save_toy()`.

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

- `def edit_toy(toy_name):`: defines the function for editing an existing toy (admin only).
- `win = tk.Toplevel(root)`: creates a new popup window.
- `win.title("Edit Toy")`: sets the window title.
- `tk.Label(win, text="Toy Name:").pack()`: displays the "Toy Name:" label.
- `name_entry = tk.Entry(win)`: creates a text entry widget for the toy name.
- `name_entry.insert(0, toy_name)`: pre-fills the entry with the current toy name.
- `name_entry.pack()`: displays the entry widget.
- `tk.Label(win, text="Price:").pack()`: displays the "Price:" label.
- `price_entry = tk.Entry(win)`: creates a text entry widget for the toy price.
- `price_entry.insert(0, toys[toy_name])`: pre-fills the entry with the current toy price.
- `price_entry.pack()`: displays the entry widget.
- `def save_changes():`: defines a nested function to save the edited toy.
- `new_name = name_entry.get()`: retrieves the new toy name.
- `new_price = price_entry.get()`: retrieves the new price.
- `if new_name == "" or new_price == "":`: checks if either field is empty.
- `messagebox.showerror(...)`: shows an error message if fields are empty.
- `else:`: executes if both fields are filled.
- `del toys[toy_name]`: removes the old toy entry from the dictionary.
- `toys[new_name] = int(new_price)`: adds the updated toy with the new name and price.
- `messagebox.showinfo(...)`: displays a success message.
- `win.destroy()`: closes the Edit Toy popup window.
- `open_admin_interface()`: refreshes the admin panel to show the updated toy.
- `tk.Button(win, text="Save Changes", command=save_changes).pack(pady=5)`: creates a Save Changes button that calls `save_changes()`.

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

- `def delete_toy(toy_name):`: defines the function for deleting a toy (admin only).
- `confirm = messagebox.askyesno(...)`: displays a confirmation dialog asking the admin to confirm deletion.
- `if confirm:`: checks if the admin clicked "Yes" on the confirmation dialog.
- `del toys[toy_name]`: removes the toy from the dictionary.
- `messagebox.showinfo(...)`: displays a success message.
- `open_admin_interface()`: refreshes the admin panel to reflect the deletion.

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

- `def go_back_to_login():`: defines the function to return to the login screen.
- `for widget in root.winfo_children(): widget.destroy()`: clears all widgets from the main window.
- `show_login_screen()`: displays the login screen.

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

- `root = tk.Tk()`: creates the main application window (the root widget).
- `root.title("Toy Shop")`: sets the window title to "Toy Shop".
- `root.geometry("600x650")`: sets the window size to 600 pixels wide and 650 pixels tall.
- `show_login_screen()`: calls the function to display the login screen on startup.
- `root.mainloop()`: starts the Tkinter event loop; keeps the window open and responsive to user interactions until closed.

## Notes

- The app stores user accounts in the MySQL `users` table.
- Passwords are stored as plain text in the database, so this is not secure for production.
- The toy inventory remains in memory only, so toy changes are lost after closing the app.
- The admin account is automatically inserted if missing.
- **NEW in v5**: The checkout screen now displays a professional payment interface with a QR code on the left and an order summary with tax calculation on the right.
- A 10% "Project Making Tax" is automatically added to the total during checkout.
- The QR code image is loaded from `QrC.jpeg` using PIL (Pillow) library.

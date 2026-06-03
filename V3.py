#---------------------------------------------
# importing packages
#---------------------------------------------

import mysql.connector as m
import tkinter as tk
from tkinter import messagebox

#-------------------------------------------------
# Creating Connection $ Confirmation of connection
#--------------------------------------------------

con = m.connect(host="localhost", user="root", password="262208", database="toyshop")

if con.is_connected():
    print("Connection successful")
else:
    print("Connection failed")

#----------------------------------------
#Create cursor so code can be read
#----------------------------------------

mycursor = con.cursor()

#----------------------------------------
#Setup Database
#----------------------------------------

mycursor.execute("CREATE DATABASE IF NOT EXISTS toyshop")
mycursor.execute("USE toyshop")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(30) NOT NULL,
        password VARCHAR(30) NOT NULL,
        is_admin VARCHAR(5) DEFAULT 'no'
    )
""")

#-------------------------------------------------
# Insert admin if not already there
#-------------------------------------------------

query = "SELECT * FROM users WHERE username = 'admin'"
mycursor.execute(query)
data = mycursor.fetchone()
if not data:
    mycursor.execute("INSERT INTO users VALUES ('admin', 'admin123', 'yes')")
    con.commit()

#-----------------------------------------
# Login Logic
#-----------------------------------------

def login():
    username = username_entry.get()
    password = password_entry.get()

    query = "SELECT * FROM users WHERE username='{}' AND password='{}'".format(username, password)
    mycursor.execute(query)
    data = mycursor.fetchone()

    if data:
        if data[2] == 'yes':  # is_admin check
            messagebox.showinfo("Login", "Welcome Admin!")
        else:
            messagebox.showinfo("Login", "Welcome {}!".format(username))
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

#---------------------------------------------------
#Signup Logic 
#---------------------------------------------------

def signup():
    username = username_entry.get()
    password = password_entry.get()

    # Check if username already exists
    query = "SELECT * FROM users WHERE username='{}'".format(username)
    mycursor.execute(query)
    data = mycursor.fetchone()

    if data:
        messagebox.showerror("Error", "Username already exists")
    else:
        mycursor.execute("INSERT INTO users VALUES ('{}', '{}', 'no')".format(username, password))
        con.commit()
        messagebox.showinfo("Signup", "Account created successfully!")

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
#-----------------------------------------------------
#Run
#-----------------------------------------------------

root = tk.Tk()
root.title("Toy Shop")
root.geometry("500x500")
show_login_screen()
root.mainloop()
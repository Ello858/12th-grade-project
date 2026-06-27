#packages
import PIL
import tkinter as tk
from PIL import Image, ImageTk

#the function to create the invoice
def PayScreen():
    tk.Label(root, text="Payment").pack()
    img = Image.open("QrC.jpeg")
    img = img.resize((200, 200))
    photo = ImageTk.PhotoImage(img)
    qr_label = tk.Label(root, image=photo)
    qr_label.image = photo    # keeps photo alive
    qr_label.pack()

#Gui
root = tk.Tk()
root.title("Invoice")
PayScreen()
root.mainloop()

from book_ui import BookApp
from tkinter import messagebox


try:
    app = BookApp()
    app.run()
except Exception:
    messagebox.showerror("Connection error",
                         "Unable to find the server."
                         "Please connect the internet "
                         "to use the application")


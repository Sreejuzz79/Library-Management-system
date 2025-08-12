import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib
from PIL import Image, ImageTk
import os

# DB CONNECTION 
def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="library_system"
    )

#  PASSWORD ENCRYPTION 
def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# BACKGROUND IMAGE SETUP 
bg_label = None  # Global variable to track background label

def set_background_image(window):
    global bg_label
    try:
        # Remove existing background if it exists
        if bg_label:
            bg_label.destroy()
            
        # Load and resize the background image
        image_path = r"C:\Users\sreej\OneDrive\Desktop\python\library.png"
        if os.path.exists(image_path):
            # Get current window size
            window.update_idletasks()
            width = window.winfo_width()
            height = window.winfo_height()
            
            # Use minimum reasonable size if window is too small
            if width < 400:
                width = 800
            if height < 300:
                height = 600
            
            # Open and resize image to fit current window size
            image = Image.open(image_path)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Create background label that fills entire window
            bg_label = tk.Label(window, image=photo)
            bg_label.image = photo  # Keep a reference
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.lower()  # Send to back so other widgets appear on top
            
            return True
        else:
            print(f"Background image not found at: {image_path}")
            return False
    except Exception as e:
        print(f"Error loading background image: {e}")
        return False

#  DYNAMIC BACKGROUND RESIZE
def on_window_resize(event):
    """Handle window resize to update background image"""
    if event.widget == window:  # Only handle main window resize
        window.after(100, lambda: set_background_image(window))  # Small delay to avoid too many calls

# NAVIGATION SYSTEM 
history = []
forward_stack = []

def navigate_to(page_func, *args):
    global history, forward_stack
    current = window.winfo_children()
    if current:
        history.append(page_func)
    forward_stack.clear()
    for widget in window.winfo_children():
        widget.destroy()
    # Set background image first
    set_background_image(window)
    page_func(*args)

def go_back():
    global history, forward_stack
    if history:
        current_page = history.pop()
        forward_stack.append(current_page)
        for widget in window.winfo_children():
            widget.destroy()
        set_background_image(window)
        history[-1]() if history else show_main_menu()

def go_forward():
    global forward_stack
    if forward_stack:
        page_func = forward_stack.pop()
        page_func()

#  STYLED FRAME HELPER 
def create_styled_frame(parent, width=400, height=300):
    """Create a semi-transparent frame for better readability over background"""
    frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
    frame.configure(highlightbackground='lightgray', highlightthickness=1)
    return frame

# MAIN MENU
def show_main_menu():
    for widget in window.winfo_children():
        widget.destroy()
    
    # Set background image
    set_background_image(window)
    
    # Create main content frame with semi-transparent background
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=350, height=250)
    
    tk.Label(main_frame, text="📚 Online Library", font=("Arial", 20, "bold"), bg='white').pack(pady=20)
    tk.Button(main_frame, text="Login as Admin", width=20, command=lambda: navigate_to(admin_login), bg='lightblue').pack(pady=10)
    tk.Button(main_frame, text="Login as User", width=20, command=lambda: navigate_to(user_login), bg='lightgreen').pack(pady=10)
    tk.Button(main_frame, text="Register", width=20, command=lambda: navigate_to(register_user), bg='lightyellow').pack(pady=10)

# REGISTER USER 
def register_user():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=300)

    tk.Label(main_frame, text="Register New User", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    tk.Label(main_frame, text="Email", bg='white').pack()
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.pack(pady=5)
    
    tk.Label(main_frame, text="Password", bg='white').pack()
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.pack(pady=5)

    def submit():
        email = email_entry.get()
        password = password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Fill all fields")
            return

        encrypted = encrypt_password(password)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("SELECT email FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                messagebox.showerror("Error", "Email already exists")
                return
            cur.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, 'user')", (email, encrypted))
            db.commit()
            messagebox.showinfo("Success", "Registration successful")
            navigate_to(show_main_menu)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    tk.Button(main_frame, text="Register", command=submit, bg='lightgreen').pack(pady=10)
    tk.Button(main_frame, text="Back", command=go_back, bg='lightgray').pack()

# ADMIN LOGIN 
def admin_login():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=300)

    tk.Label(main_frame, text="Admin Login", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    tk.Label(main_frame, text="Email", bg='white').pack()
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.pack(pady=5)
    
    tk.Label(main_frame, text="Password", bg='white').pack()
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.pack(pady=5)

    def login():
        email = email_entry.get()
        password = password_entry.get()
        encrypted = encrypt_password(password)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("SELECT role FROM users WHERE email=%s AND password=%s", (email, encrypted))
            result = cur.fetchone()
            if result and result[0] == "admin":
                navigate_to(admin_dashboard)
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    tk.Button(main_frame, text="Login", command=login, bg='lightblue').pack(pady=10)
    tk.Button(main_frame, text="Back", command=go_back, bg='lightgray').pack()

# USER LOGIN 
def user_login():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=300)

    tk.Label(main_frame, text="User Login", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    tk.Label(main_frame, text="Email", bg='white').pack()
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.pack(pady=5)
    
    tk.Label(main_frame, text="Password", bg='white').pack()
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.pack(pady=5)

    def login():
        email = email_entry.get()
        password = password_entry.get()
        encrypted = encrypt_password(password)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("SELECT user_id, role FROM users WHERE email=%s AND password=%s", (email, encrypted))
            result = cur.fetchone()
            if result and result[1] == "user":
                navigate_to(user_dashboard, result[0])
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    tk.Button(main_frame, text="Login", command=login, bg='lightgreen').pack(pady=10)
    tk.Button(main_frame, text="Back", command=go_back, bg='lightgray').pack()

# ADMIN DASHBOARD 
def admin_dashboard():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)

    # Create main container with background
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="Admin Dashboard", font=("Arial", 16, "bold"), bg='white').pack(pady=10)

    # Create a notebook for tabs
    notebook = ttk.Notebook(container)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Books tab
    books_frame = ttk.Frame(notebook)
    notebook.add(books_frame, text="Books Management")

    # Users tab
    users_frame = ttk.Frame(notebook)
    notebook.add(users_frame, text="Users Management")

    # BOOKS TAB 
    tk.Label(books_frame, text="Books Management", font=("Arial", 14, "bold")).pack(pady=5)
    
    books_table = ttk.Treeview(books_frame, columns=("ID", "Title", "Author", "Total", "Available"), show="headings", height=10)
    books_table.heading("ID", text="Book ID")
    books_table.heading("Title", text="Title")
    books_table.heading("Author", text="Author")
    books_table.heading("Total", text="Total Copies")
    books_table.heading("Available", text="Available Copies")
    books_table.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_books_table():
        for item in books_table.get_children():
            books_table.delete(item)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("SELECT book_id, title, author, total_copies, available_copies FROM books")
            for row in cur.fetchall():
                books_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    refresh_books_table()

    # Book action buttons
    book_buttons_frame = tk.Frame(books_frame)
    book_buttons_frame.pack(pady=10)

    def add_book():
        navigate_to(admin_add_book)

    def edit_book():
        selected = books_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book to edit")
            return
        book_data = books_table.item(selected)["values"]
        navigate_to(admin_edit_book, book_data)

    def delete_book():
        selected = books_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book to delete")
            return
        book_id = books_table.item(selected)["values"][0]
        book_title = books_table.item(selected)["values"][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{book_title}'?"):
            try:
                db = db_connection()
                cur = db.cursor()
                # Check if book is currently borrowed
                cur.execute("SELECT COUNT(*) FROM borrowed WHERE book_id=%s AND return_date IS NULL", (book_id,))
                if cur.fetchone()[0] > 0:
                    messagebox.showerror("Error", "Cannot delete book that is currently borrowed")
                    return
                
                cur.execute("DELETE FROM books WHERE book_id=%s", (book_id,))
                db.commit()
                messagebox.showinfo("Success", "Book deleted successfully")
                refresh_books_table()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                db.close()

    def view_borrowed():
        selected = books_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book")
            return
        book_id = books_table.item(selected)["values"][0]
        navigate_to(admin_view_borrowed, book_id)

    tk.Button(book_buttons_frame, text="Add Book", command=add_book, width=12, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="Edit Book", command=edit_book, width=12, bg='lightyellow').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="Delete Book", command=delete_book, width=12, bg='lightcoral').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="View Borrowed", command=view_borrowed, width=12, bg='lightblue').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="All Borrowed Books", command=lambda: navigate_to(admin_all_borrowed), width=15, bg='lightcyan').pack(side="left", padx=5)

    # USERS TAB 
    tk.Label(users_frame, text="Users Management", font=("Arial", 14, "bold")).pack(pady=5)
    
    users_table = ttk.Treeview(users_frame, columns=("ID", "Email", "Role"), show="headings", height=10)
    users_table.heading("ID", text="User ID")
    users_table.heading("Email", text="Email")
    users_table.heading("Role", text="Role")
    users_table.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_users_table():
        for item in users_table.get_children():
            users_table.delete(item)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("SELECT user_id, email, role FROM users")
            for row in cur.fetchall():
                users_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    refresh_users_table()

    # User action buttons
    user_buttons_frame = tk.Frame(users_frame)
    user_buttons_frame.pack(pady=10)

    def add_user():
        navigate_to(admin_add_user)

    def edit_user():
        selected = users_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user to edit")
            return
        user_data = users_table.item(selected)["values"]
        navigate_to(admin_edit_user, user_data)

    def delete_user():
        selected = users_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user to delete")
            return
        user_id = users_table.item(selected)["values"][0]
        user_email = users_table.item(selected)["values"][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{user_email}'?"):
            try:
                db = db_connection()
                cur = db.cursor()
                # Check if user has borrowed books
                cur.execute("SELECT COUNT(*) FROM borrowed WHERE user_id=%s AND return_date IS NULL", (user_id,))
                if cur.fetchone()[0] > 0:
                    messagebox.showerror("Error", "Cannot delete user who has borrowed books")
                    return
                
                cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
                db.commit()
                messagebox.showinfo("Success", "User deleted successfully")
                refresh_users_table()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                db.close()

    tk.Button(user_buttons_frame, text="Add User", command=add_user, width=12, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(user_buttons_frame, text="Edit User", command=edit_user, width=12, bg='lightyellow').pack(side="left", padx=5)
    tk.Button(user_buttons_frame, text="Delete User", command=delete_user, width=12, bg='lightcoral').pack(side="left", padx=5)
    tk.Button(user_buttons_frame, text="View User Books", command=lambda: navigate_to(admin_user_borrowed), width=15, bg='lightcyan').pack(side="left", padx=5)

    # Navigation buttons
    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=10)
    tk.Button(nav_frame, text="Back", command=go_back, bg='lightgray').pack(side="left", padx=5)
    if forward_stack:
        tk.Button(nav_frame, text="Forward", command=go_forward, bg='lightgray').pack(side="left", padx=5)

# ADMIN ADD BOOK 
def admin_add_book() :
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=350)

    tk.Label(main_frame, text="Add New Book", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(pady=20)
    
    tk.Label(form_frame, text="Title:", bg='white').grid(row=0, column=0, sticky="e", padx=5, pady=5)
    title_entry = tk.Entry(form_frame, width=30)
    title_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Author:", bg='white').grid(row=1, column=0, sticky="e", padx=5, pady=5)
    author_entry = tk.Entry(form_frame, width=30)
    author_entry.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Total Copies:", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    copies_entry = tk.Entry(form_frame, width=30)
    copies_entry.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        try:
            total_copies = int(copies_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Total copies must be a number")
            return
            
        if not title or not author or total_copies <= 0:
            messagebox.showerror("Error", "Please fill all fields with valid data")
            return

        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("INSERT INTO books (title, author, total_copies, available_copies) VALUES (%s, %s, %s, %s)", 
                       (title, author, total_copies, total_copies))
            db.commit()
            messagebox.showinfo("Success", "Book added successfully")
            navigate_to(admin_dashboard)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Add Book", command=submit, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=lambda: navigate_to(admin_dashboard), bg='lightgray').pack(side="left", padx=5)

# ADMIN EDIT BOOK 
def admin_edit_book(book_data):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=350)

    tk.Label(main_frame, text="Edit Book", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(pady=20)
    
    tk.Label(form_frame, text="Title:", bg='white').grid(row=0, column=0, sticky="e", padx=5, pady=5)
    title_entry = tk.Entry(form_frame, width=30)
    title_entry.insert(0, book_data[1])
    title_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Author:", bg='white').grid(row=1, column=0, sticky="e", padx=5, pady=5)
    author_entry = tk.Entry(form_frame, width=30)
    author_entry.insert(0, book_data[2])
    author_entry.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Total Copies:", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    copies_entry = tk.Entry(form_frame, width=30)
    copies_entry.insert(0, str(book_data[3]))
    copies_entry.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        try:
            total_copies = int(copies_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Total copies must be a number")
            return
            
        if not title or not author or total_copies <= 0:
            messagebox.showerror("Error", "Please fill all fields with valid data")
            return

        try:
            db = db_connection()
            cur = db.cursor()
            # Calculate new available copies
            borrowed_count = book_data[3] - book_data[4]  # total - available = borrowed
            new_available = total_copies - borrowed_count
            
            if new_available < 0:
                messagebox.showerror("Error", "Total copies cannot be less than currently borrowed copies")
                return
            
            cur.execute("UPDATE books SET title=%s, author=%s, total_copies=%s, available_copies=%s WHERE book_id=%s", 
                       (title, author, total_copies, new_available, book_data[0]))
            db.commit()
            messagebox.showinfo("Success", "Book updated successfully")
            navigate_to(admin_dashboard)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Update Book", command=submit, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=lambda: navigate_to(admin_dashboard), bg='lightgray').pack(side="left", padx=5)

# ADMIN ADD USER
def admin_add_user():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=350)

    tk.Label(main_frame, text="Add New User", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(pady=20)
    
    tk.Label(form_frame, text="Email:", bg='white').grid(row=0, column=0, sticky="e", padx=5, pady=5)
    email_entry = tk.Entry(form_frame, width=30)
    email_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Password:", bg='white').grid(row=1, column=0, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(form_frame, width=30, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Role:", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    role_var = tk.StringVar(value="user")
    role_combo = ttk.Combobox(form_frame, textvariable=role_var, values=["user", "admin"], state="readonly")
    role_combo.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        email = email_entry.get().strip()
        password = password_entry.get()
        role = role_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        encrypted = encrypt_password(password)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("SELECT email FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                messagebox.showerror("Error", "Email already exists")
                return
            
            cur.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", (email, encrypted, role))
            db.commit()
            messagebox.showinfo("Success", "User added successfully")
            navigate_to(admin_dashboard)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Add User", command=submit, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=lambda: navigate_to(admin_dashboard), bg='lightgray').pack(side="left", padx=5)

# ADMIN EDIT USER 
def admin_edit_user(user_data):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=400)

    tk.Label(main_frame, text="Edit User", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(pady=20)
    
    tk.Label(form_frame, text="Email:", bg='white').grid(row=0, column=0, sticky="e", padx=5, pady=5)
    email_entry = tk.Entry(form_frame, width=30)
    email_entry.insert(0, user_data[1])
    email_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="New Password:", bg='white').grid(row=1, column=0, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(form_frame, width=30, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(form_frame, text="(Leave blank to keep current)", font=("Arial", 8), bg='white').grid(row=1, column=2, padx=5)
    
    tk.Label(form_frame, text="Role:", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    role_var = tk.StringVar(value=user_data[2])
    role_combo = ttk.Combobox(form_frame, textvariable=role_var, values=["user", "admin"], state="readonly")
    role_combo.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        email = email_entry.get().strip()
        password = password_entry.get()
        role = role_var.get()
        
        if not email:
            messagebox.showerror("Error", "Email cannot be empty")
            return

        try:
            db = db_connection()
            cur = db.cursor()
            
            # Check if email exists for other users
            cur.execute("SELECT user_id FROM users WHERE email=%s AND user_id != %s", (email, user_data[0]))
            if cur.fetchone():
                messagebox.showerror("Error", "Email already exists for another user")
                return
            
            if password:  # Update password if provided
                encrypted = encrypt_password(password)
                cur.execute("UPDATE users SET email=%s, password=%s, role=%s WHERE user_id=%s", 
                           (email, encrypted, role, user_data[0]))
            else:  # Keep current password
                cur.execute("UPDATE users SET email=%s, role=%s WHERE user_id=%s", 
                           (email, role, user_data[0]))
            
            db.commit()
            messagebox.showinfo("Success", "User updated successfully")
            navigate_to(admin_dashboard)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    button_frame = tk.Frame(main_frame, bg='white')
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Update User", command=submit, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=lambda: navigate_to(admin_dashboard), bg='lightgray').pack(side="left", padx=5)

# ADMIN ALL BORROWED BOOKS 
def admin_all_borrowed():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="All Borrowed Books Overview", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    table = ttk.Treeview(container, columns=("BookID", "Title", "Author", "User", "Email", "BorrowDate", "Total", "Available"), show="headings", height=15)
    table.heading("BookID", text="Book ID")
    table.heading("Title", text="Book Title")
    table.heading("Author", text="Author")
    table.heading("User", text="User ID")
    table.heading("Email", text="User Email")
    table.heading("BorrowDate", text="Borrow Date")
    table.heading("Total", text="Total Copies")
    table.heading("Available", text="Available")
    
    # Adjust column widths
    table.column("BookID", width=80)
    table.column("Title", width=150)
    table.column("Author", width=120)
    table.column("User", width=80)
    table.column("Email", width=150)
    table.column("BorrowDate", width=100)
    table.column("Total", width=80)
    table.column("Available", width=80)
    
    table.pack(fill="both", expand=True, padx=10, pady=10)

    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("""
            SELECT b.book_id, b.title, b.author, u.user_id, u.email, 
                   bb.borrow_date, b.total_copies, b.available_copies
            FROM borrowed bb
            JOIN books b ON bb.book_id = b.book_id
            JOIN users u ON bb.user_id = u.user_id
            WHERE bb.return_date IS NULL
            ORDER BY bb.borrow_date DESC
        """)
        for row in cur.fetchall():
            # Format date if it exists
            row_list = list(row)
            if row_list[5]:  # borrow_date
                row_list[5] = row_list[5].strftime("%Y-%m-%d") if hasattr(row_list[5], 'strftime') else str(row_list[5])
            table.insert("", "end", values=row_list)
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        db.close()

    # Summary frame
    summary_frame = tk.Frame(container, bg='white')
    summary_frame.pack(pady=10)
    
    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM borrowed WHERE return_date IS NULL")
        total_borrowed = cur.fetchone()[0]
        tk.Label(summary_frame, text=f"Total Currently Borrowed Books: {total_borrowed}", 
                font=("Arial", 12, "bold"), fg="blue", bg='white').pack()
    except Exception as e:
        pass
    finally:
        db.close()

    tk.Button(container, text="Back", command=go_back, bg='lightgray').pack(pady=5)

# ADMIN USER BORROWED BOOKS 
def admin_user_borrowed():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="View User's Borrowed Books", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    # User selection frame
    select_frame = tk.Frame(container, bg='white')
    select_frame.pack(pady=10)
    
    tk.Label(select_frame, text="Select User:", font=("Arial", 12), bg='white').pack(side="left", padx=5)
    user_var = tk.StringVar()
    user_combo = ttk.Combobox(select_frame, textvariable=user_var, width=30, state="readonly")
    user_combo.pack(side="left", padx=5)
    
    # Populate users dropdown
    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("SELECT user_id, email FROM users WHERE role='user'")
        users = cur.fetchall()
        user_options = [f"{user[0]} - {user[1]}" for user in users]
        user_combo['values'] = user_options
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        db.close()
    
    table = ttk.Treeview(container, columns=("BookID", "Title", "Author", "BorrowDate", "Status"), show="headings", height=12)
    table.heading("BookID", text="Book ID")
    table.heading("Title", text="Book Title")
    table.heading("Author", text="Author")
    table.heading("BorrowDate", text="Borrow Date")
    table.heading("Status", text="Status")
    table.pack(fill="both", expand=True, padx=10, pady=10)

    def load_user_books():
        if not user_var.get():
            messagebox.showerror("Error", "Please select a user")
            return
            
        user_id = user_var.get().split(" - ")[0]
        
        # Clear existing items
        for item in table.get_children():
            table.delete(item)
            
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("""
                SELECT b.book_id, b.title, b.author, bb.borrow_date, 
                       CASE WHEN bb.return_date IS NULL THEN 'Borrowed' ELSE 'Returned' END as status
                FROM borrowed bb
                JOIN books b ON bb.book_id = b.book_id
                WHERE bb.user_id = %s
                ORDER BY bb.borrow_date DESC
            """, (user_id,))
            
            for row in cur.fetchall():
                row_list = list(row)
                if row_list[3]:  # borrow_date
                    row_list[3] = row_list[3].strftime("%Y-%m-%d") if hasattr(row_list[3], 'strftime') else str(row_list[3])
                table.insert("", "end", values=row_list)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    tk.Button(select_frame, text="Load Books", command=load_user_books, bg='lightblue').pack(side="left", padx=5)
    tk.Button(container, text="Back", command=go_back, bg='lightgray').pack(pady=5)

def admin_view_borrowed(book_id):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="Borrowed Users", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    table = ttk.Treeview(container, columns=("User", "Email", "Borrow Date"), show="headings")
    table.heading("User", text="User ID")
    table.heading("Email", text="Email")
    table.heading("Borrow Date", text="Borrow Date")
    table.pack(fill="both", expand=True)

    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("""
            SELECT u.user_id, u.email, bb.borrow_date
            FROM borrowed bb
            JOIN users u ON bb.user_id = u.user_id
            WHERE bb.book_id = %s AND bb.return_date IS NULL
        """, (book_id,))
        for row in cur.fetchall():
            table.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        db.close()

    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=10)
    tk.Button(nav_frame, text="Back", command=go_back, bg='lightgray').pack(side="left", padx=5)
    if forward_stack:
        tk.Button(nav_frame, text="Forward", command=go_forward, bg='lightgray').pack(side="left", padx=5)

# USER DASHBOARD 
def user_dashboard(user_id):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="User Dashboard", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    table = ttk.Treeview(container, columns=("ID", "Title", "Total", "Available"), show="headings")
    table.heading("ID", text="Book ID")
    table.heading("Title", text="Title")
    table.heading("Total", text="Total Copies")
    table.heading("Available", text="Available Copies")
    table.pack(fill="both", expand=True)

    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("SELECT book_id, title, total_copies, available_copies FROM books")
        for row in cur.fetchall():
            table.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        db.close()

    def borrow_book():
        selected = table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a book")
            return
        book_id, _, _, available = table.item(selected)["values"]
        if available <= 0:
            messagebox.showerror("Error", "No copies available")
            return
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("INSERT INTO borrowed (user_id, book_id, borrow_date) VALUES (%s, %s, NOW())", (user_id, book_id))
            cur.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id=%s", (book_id,))
            db.commit()
            messagebox.showinfo("Success", "Book borrowed successfully")
            navigate_to(user_dashboard, user_id)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    def return_book():
        selected = table.selection()
        if not selected:
            messagebox.showerror("Error", "Select a book")
            return
        book_id = table.item(selected)["values"][0]
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("""
                UPDATE borrowed 
                SET return_date = NOW() 
                WHERE user_id=%s AND book_id=%s AND return_date IS NULL
            """, (user_id, book_id))
            cur.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id=%s", (book_id,))
            db.commit()
            messagebox.showinfo("Success", "Book returned successfully")
            navigate_to(user_dashboard, user_id)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    button_frame = tk.Frame(container, bg='white')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Borrow Book", command=borrow_book, bg='lightgreen').pack(pady=5)
    tk.Button(button_frame, text="Return Book", command=return_book, bg='lightcoral').pack(pady=5)
    tk.Button(button_frame, text="My Borrowed Books", command=lambda: navigate_to(user_borrowed_books, user_id), bg='lightblue').pack(pady=5)
    
    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=5)
    tk.Button(nav_frame, text="Back", command=go_back, bg='lightgray').pack(side="left", padx=5)
    if forward_stack:
        tk.Button(nav_frame, text="Forward", command=go_forward, bg='lightgray').pack(side="left", padx=5)

# USER BORROWED BOOKS 
def user_borrowed_books(user_id):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="My Borrowed Books", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    # Create notebook for current and history
    notebook = ttk.Notebook(container)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Currently borrowed tab
    current_frame = ttk.Frame(notebook)
    notebook.add(current_frame, text="Currently Borrowed")

    # History tab
    history_frame = ttk.Frame(notebook)
    notebook.add(history_frame, text="Borrowing History")

    # CURRENTLY BORROWED TAB 
    tk.Label(current_frame, text="Books Currently in Your Possession", font=("Arial", 12, "bold")).pack(pady=5)
    
    current_table = ttk.Treeview(current_frame, columns=("BookID", "Title", "Author", "BorrowDate", "DaysHeld"), show="headings", height=10)
    current_table.heading("BookID", text="Book ID")
    current_table.heading("Title", text="Title")
    current_table.heading("Author", text="Author")
    current_table.heading("BorrowDate", text="Borrow Date")
    current_table.heading("DaysHeld", text="Days Held")
    current_table.pack(fill="both", expand=True, padx=5, pady=5)

    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("""
            SELECT b.book_id, b.title, b.author, bb.borrow_date,
                   DATEDIFF(NOW(), bb.borrow_date) as days_held
            FROM borrowed bb
            JOIN books b ON bb.book_id = b.book_id
            WHERE bb.user_id = %s AND bb.return_date IS NULL
            ORDER BY bb.borrow_date DESC
        """, (user_id,))
        
        current_count = 0
        for row in cur.fetchall():
            row_list = list(row)
            if row_list[3]:  # borrow_date
                row_list[3] = row_list[3].strftime("%Y-%m-%d") if hasattr(row_list[3], 'strftime') else str(row_list[3])
            current_table.insert("", "end", values=row_list)
            current_count += 1
            
        tk.Label(current_frame, text=f"Total Currently Borrowed: {current_count}", 
                font=("Arial", 10, "bold"), fg="blue").pack(pady=5)
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        db.close()

    # Quick return function for current tab
    def quick_return():
        selected = current_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book to return")
            return
        book_id = current_table.item(selected)["values"][0]
        book_title = current_table.item(selected)["values"][1]
        
        if messagebox.askyesno("Confirm Return", f"Return '{book_title}'?"):
            try:
                db = db_connection()
                cur = db.cursor()
                cur.execute("""
                    UPDATE borrowed 
                    SET return_date = NOW() 
                    WHERE user_id=%s AND book_id=%s AND return_date IS NULL
                """, (user_id, book_id))
                cur.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id=%s", (book_id,))
                db.commit()
                messagebox.showinfo("Success", "Book returned successfully")
                navigate_to(user_borrowed_books, user_id)  # Refresh the page
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                db.close()

    tk.Button(current_frame, text="Return Selected Book", command=quick_return, bg='lightcoral').pack(pady=5)

    #  HISTORY TAB 
    tk.Label(history_frame, text="Complete Borrowing History", font=("Arial", 12, "bold")).pack(pady=5)
    
    history_table = ttk.Treeview(history_frame, columns=("BookID", "Title", "Author", "BorrowDate", "ReturnDate", "Status"), show="headings", height=10)
    history_table.heading("BookID", text="Book ID")
    history_table.heading("Title", text="Title")
    history_table.heading("Author", text="Author")
    history_table.heading("BorrowDate", text="Borrow Date")
    history_table.heading("ReturnDate", text="Return Date")
    history_table.heading("Status", text="Status")
    
    # Adjust column widths
    history_table.column("BookID", width=80)
    history_table.column("Title", width=150)
    history_table.column("Author", width=120)
    history_table.column("BorrowDate", width=100)
    history_table.column("ReturnDate", width=100)
    history_table.column("Status", width=100)
    
    history_table.pack(fill="both", expand=True, padx=5, pady=5)

    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("""
            SELECT b.book_id, b.title, b.author, bb.borrow_date, bb.return_date,
                   CASE WHEN bb.return_date IS NULL THEN 'Currently Borrowed' ELSE 'Returned' END as status
            FROM borrowed bb
            JOIN books b ON bb.book_id = b.book_id
            WHERE bb.user_id = %s
            ORDER BY bb.borrow_date DESC
        """, (user_id,))
        
        total_count = 0
        returned_count = 0
        for row in cur.fetchall():
            row_list = list(row)

            if row_list[3]:  
                row_list[3] = row_list[3].strftime("%Y-%m-%d") if hasattr(row_list[3], 'strftime') else str(row_list[3])
            if row_list[4]:  
                row_list[4] = row_list[4].strftime("%Y-%m-%d") if hasattr(row_list[4], 'strftime') else str(row_list[4])
                returned_count += 1
            else:
                row_list[4] = "Not Yet Returned"
            
            history_table.insert("", "end", values=row_list)
            total_count += 1

        summary_frame = tk.Frame(history_frame)
        summary_frame.pack(pady=5)
        tk.Label(summary_frame, text=f"Total Books Borrowed: {total_count}", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Label(summary_frame, text=f"Books Returned: {returned_count}", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Label(summary_frame, text=f"Currently Holding: {total_count - returned_count}", font=("Arial", 10, "bold"), fg="red").pack(side="left", padx=10)
        
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        db.close()

    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=10)
    tk.Button(nav_frame, text="Back to Dashboard", command=lambda: navigate_to(user_dashboard, user_id), bg='lightgray').pack(side="left", padx=5)

#  MAIN WINDOW SETUP 
window = tk.Tk()
window.title("Library Management System")
window.geometry("800x600")
window.configure(bg='white')

# Enable window resizing
window.resizable(True, True)

# Bind resize event to update background
window.bind('<Configure>', on_window_resize)


set_background_image(window)
show_main_menu()
window.mainloop()
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

    tk.Label(main_frame, text="Full Name", bg='white').pack()
    name_entry = tk.Entry(main_frame, width=30)
    name_entry.pack(pady=5)

    tk.Label(main_frame, text="Email", bg='white').pack()
    email_entry = tk.Entry(main_frame, width=30)
    email_entry.pack(pady=5)
    
    tk.Label(main_frame, text="Password", bg='white').pack()
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.pack(pady=5)

    def submit():
        full_name = name_entry.get()  
        email = email_entry.get()
        password = password_entry.get()
        if not full_name or not email or not password:  
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
            # Ensure parameters are passed as a tuple or list
            cur.execute("INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, %s)", (full_name, email, encrypted, 'user'))  
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

# ADMIN DASHBOARD - FIXED TO SHOW ALL BOOKS INCLUDING FULLY BORROWED ONES
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

    # BOOKS TAB - FIXED TO SHOW ALL BOOKS
    tk.Label(books_frame, text="Books Management", font=("Arial", 14, "bold")).pack(pady=5)
    
    books_table = ttk.Treeview(books_frame, columns=("ID", "Title", "Author", "Category", "Total", "Available"), show="headings", height=10)
    books_table.heading("ID", text="Book ID")
    books_table.heading("Title", text="Title")
    books_table.heading("Author", text="Author")
    books_table.heading("Category", text="Category")
    books_table.heading("Total", text="Total Copies")
    books_table.heading("Available", text="Available Copies")
    books_table.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_books_table():
        for item in books_table.get_children():
             books_table.delete(item)
        try:
          db = db_connection()
          cur = db.cursor()

        # FIXED: Removed the condition that hides books with 0 available copies
          cur.execute("""
            SELECT b.book_id, b.title, b.author, c.category_name, b.total_copies, b.available_copies
            FROM books b
            JOIN categories c ON b.category_id = c.category_id
            ORDER BY c.category_name, b.title
        """)

          for row in cur.fetchall():
                # Color code rows based on availability
                item = books_table.insert("", "end", values=row)
                # If no copies available, you could add visual indication here
                if row[5] == 0:  # available_copies is 0
                    books_table.set(item, "Available", "0 (All Borrowed)")
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
        # Clean the available copies display for editing
        if isinstance(book_data[5], str) and "All Borrowed" in str(book_data[5]):
            book_data = list(book_data)
            book_data[5] = 0
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

    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            navigate_to(show_main_menu)

    tk.Button(book_buttons_frame, text="Add Book", command=add_book, width=12, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="Edit Book", command=edit_book, width=12, bg='lightyellow').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="Delete Book", command=delete_book, width=12, bg='lightcoral').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="View Borrowed", command=view_borrowed, width=12, bg='lightblue').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="All Borrowed Books", command=lambda: navigate_to(admin_all_borrowed), width=15, bg='lightcyan').pack(side="left", padx=5)
    tk.Button(book_buttons_frame, text="Logout", command=logout, width=12, bg='lightgray').pack(side="left", padx=5)

    # USERS TAB - FIXED COLUMN ORDER
    tk.Label(users_frame, text="Users Management", font=("Arial", 14, "bold")).pack(pady=5)
    
    users_table = ttk.Treeview(users_frame, columns=("ID", "Full_Name", "Email", "Role"), show="headings", height=10)
    users_table.heading("ID", text="User ID")
    users_table.heading("Full_Name", text="Full Name")
    users_table.heading("Email", text="Email")
    users_table.heading("Role", text="Role")
    users_table.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_users_table():
        for item in users_table.get_children():
            users_table.delete(item)
        try:
            db = db_connection()
            cur = db.cursor()
            # FIXED: Match the column order with table headers
            cur.execute("SELECT user_id, full_name, email, role FROM users WHERE role='user'")
            users = cur.fetchall()
            for row in users:
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
        user_email = users_table.item(selected)["values"][2]  # Fixed index for email
        
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

    def logout_users():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            navigate_to(show_main_menu)

    tk.Button(user_buttons_frame, text="Add User", command=add_user, width=12, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(user_buttons_frame, text="Edit User", command=edit_user, width=12, bg='lightyellow').pack(side="left", padx=5)
    tk.Button(user_buttons_frame, text="Delete User", command=delete_user, width=12, bg='lightcoral').pack(side="left", padx=5)
    tk.Button(user_buttons_frame, text="View User Books", command=lambda: navigate_to(admin_user_borrowed), width=15, bg='lightcyan').pack(side="left", padx=5)
    tk.Button(user_buttons_frame, text="Logout", command=logout_users, width=12, bg='lightgray').pack(side="left", padx=5)

    # Navigation buttons
    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=10)
    tk.Button(nav_frame, text="Back", command=go_back, bg='lightgray').pack(side="left", padx=5)
    if forward_stack:
        tk.Button(nav_frame, text="Forward", command=go_forward, bg='lightgray').pack(side="left", padx=5)

# ADMIN EDIT BOOK - FIXED
def admin_edit_book(book_data):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=400)

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

    tk.Label(form_frame, text="Category:", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    
    # Get categories and current category
    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("SELECT category_name FROM categories")
        categories = [row[0] for row in cur.fetchall()]
        current_category = book_data[3]  # category name from display
        db.close()
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        categories = []
        current_category = ""
    
    category_var = tk.StringVar(value=current_category)
    category_combo = ttk.Combobox(form_frame, textvariable=category_var, values=categories)
    category_combo.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Total Copies:", bg='white').grid(row=3, column=0, sticky="e", padx=5, pady=5)
    copies_entry = tk.Entry(form_frame, width=30)
    copies_entry.insert(0, book_data[4])
    copies_entry.grid(row=3, column=1, padx=5, pady=5)

    def submit():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        category_name = category_var.get().strip()
        try:
            total_copies = int(copies_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Total copies must be a number")
            return
            
        if not title or not author or not category_name or total_copies <= 0:
            messagebox.showerror("Error", "Please fill all fields with valid data")
            return

        try:
            db = db_connection()
            cur = db.cursor()
            
            # Check if title already exists for other books
            cur.execute("SELECT book_id FROM books WHERE title=%s AND book_id != %s", (title, book_data[0]))
            if cur.fetchone():
                messagebox.showerror("Error", "Book title already exists")
                return
            
            # Get or create category
            cur.execute("SELECT category_id FROM categories WHERE category_name=%s", (category_name,))
            category = cur.fetchone()
            if category:
                category_id = category[0]
            else:
                cur.execute("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
                category_id = cur.lastrowid
                
            # Calculate available copies difference
            old_total = book_data[4]
            old_available = book_data[5]
            difference = total_copies - old_total
            new_available = old_available + difference
            
            # Make sure available copies don't go negative
            if new_available < 0:
                new_available = 0
            
            cur.execute("UPDATE books SET title=%s, author=%s, category_id=%s, total_copies=%s, available_copies=%s WHERE book_id=%s", 
                       (title, author, category_id, total_copies, new_available, book_data[0]))
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

# ADMIN ADD BOOK - FIXED (removed duplicate)
def admin_add_book():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=400)

    tk.Label(main_frame, text="Add New Book", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(pady=20)
    
    tk.Label(form_frame, text="Title:", bg='white').grid(row=0, column=0, sticky="e", padx=5, pady=5)
    title_entry = tk.Entry(form_frame, width=30)
    title_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Author:", bg='white').grid(row=1, column=0, sticky="e", padx=5, pady=5)
    author_entry = tk.Entry(form_frame, width=30)
    author_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Category:", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    category_entry = tk.Entry(form_frame, width=30)
    category_entry.grid(row=2, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Total Copies:", bg='white').grid(row=3, column=0, sticky="e", padx=5, pady=5)
    copies_entry = tk.Entry(form_frame, width=30)
    copies_entry.grid(row=3, column=1, padx=5, pady=5)

    def submit():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        category_name = category_entry.get().strip()
        try:
            total_copies = int(copies_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Total copies must be a number")
            return
            
        if not title or not author or not category_name or total_copies <= 0:
            messagebox.showerror("Error", "Please fill all fields with valid data")
            return

        try:
            db = db_connection()
            cur = db.cursor()
            
            # Check if title already exists
            cur.execute("SELECT book_id FROM books WHERE title=%s", (title,))
            if cur.fetchone():
                messagebox.showerror("Error", "Book title already exists")
                return
            
            # Check if category exists, if not create it
            cur.execute("SELECT category_id FROM categories WHERE category_name=%s", (category_name,))
            category = cur.fetchone()
            if category:
                category_id = category[0]
            else:
                cur.execute("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
                category_id = cur.lastrowid
            
            cur.execute("INSERT INTO books (title, author, category_id, total_copies, available_copies) VALUES (%s, %s, %s, %s, %s)", 
                       (title, author, category_id, total_copies, total_copies))
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

# ADMIN ADD USER - COMPLETED
def admin_add_user():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    main_frame = create_styled_frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=350)

    tk.Label(main_frame, text="Add New User", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(pady=20)
    
    tk.Label(form_frame, text="Full Name:", bg='white').grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_entry = tk.Entry(form_frame, width=30)
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Email:", bg='white').grid(row=1, column=0, sticky="e", padx=5, pady=5)
    email_entry = tk.Entry(form_frame, width=30)
    email_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Password:", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(form_frame, width=30, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        full_name = name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        
        if not full_name or not email or not password:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            db = db_connection()
            cur = db.cursor()
            
            # Check if email already exists
            cur.execute("SELECT email FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                messagebox.showerror("Error", "Email already exists")
                return
            
            encrypted_password = encrypt_password(password)
            cur.execute("INSERT INTO users (full_name, email, password, role) VALUES (%s, %s, %s, %s)", 
                       (full_name, email, encrypted_password, 'user'))
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
    main_frame.place(relx=0.5, rely=0.5, anchor='center', width=450, height=350)

    tk.Label(main_frame, text="Edit User", font=("Arial", 16, "bold"), bg='white').pack(pady=10)
    
    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(pady=20)
    
    tk.Label(form_frame, text="Full Name:", bg='white').grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_entry = tk.Entry(form_frame, width=30)
    name_entry.insert(0, user_data[1])
    name_entry.grid(row=0, column=1, padx=5, pady=5)
    
    tk.Label(form_frame, text="Email:", bg='white').grid(row=1, column=0, sticky="e", padx=5, pady=5)
    email_entry = tk.Entry(form_frame, width=30)
    email_entry.insert(0, user_data[2])
    email_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="New Password (leave blank to keep current):", bg='white').grid(row=2, column=0, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(form_frame, width=30, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        full_name = name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        
        if not full_name or not email:
            messagebox.showerror("Error", "Name and email are required")
            return

        try:
            db = db_connection()
            cur = db.cursor()
            
            # Check if email already exists for other users
            cur.execute("SELECT user_id FROM users WHERE email=%s AND user_id != %s", (email, user_data[0]))
            if cur.fetchone():
                messagebox.showerror("Error", "Email already exists")
                return
            
            if password:
                encrypted_password = encrypt_password(password)
                cur.execute("UPDATE users SET full_name=%s, email=%s, password=%s WHERE user_id=%s", 
                           (full_name, email, encrypted_password, user_data[0]))
            else:
                cur.execute("UPDATE users SET full_name=%s, email=%s WHERE user_id=%s", 
                           (full_name, email, user_data[0]))
            
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

# ADMIN VIEW BORROWED BOOKS FOR SPECIFIC BOOK
def admin_view_borrowed(book_id):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="Borrowed Books Report", font=("Arial", 16, "bold"), bg='white').pack(pady=10)

    # Create treeview for borrowed books
    borrowed_table = ttk.Treeview(container, columns=("ID", "User", "Email", "Borrow_Date", "Due_Date", "Status"), show="headings", height=15)
    borrowed_table.heading("ID", text="Borrow ID")
    borrowed_table.heading("User", text="User Name")
    borrowed_table.heading("Email", text="Email")
    borrowed_table.heading("Borrow_Date", text="Borrow Date")
    borrowed_table.heading("Due_Date", text="Due Date")
    borrowed_table.heading("Status", text="Status")
    borrowed_table.pack(fill="both", expand=True, padx=10, pady=10)

    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("""
            SELECT br.borrow_id, u.full_name, u.email, br.borrow_date, br.due_date,
                   CASE WHEN br.return_date IS NULL THEN 'Borrowed' ELSE 'Returned' END as status
            FROM borrowed br
            JOIN users u ON br.user_id = u.user_id
            WHERE br.book_id = %s
            ORDER BY br.borrow_date DESC
        """, (book_id,))
        
        for row in cur.fetchall():
            borrowed_table.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
    finally:
        db.close()

    # Navigation buttons
    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=10)
    tk.Button(nav_frame, text="Back to Dashboard", command=lambda: navigate_to(admin_dashboard), bg='lightgray').pack()

# ADMIN VIEW ALL BORROWED BOOKS
def admin_all_borrowed():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="All Borrowed Books", font=("Arial", 16, "bold"), bg='white').pack(pady=10)

    # Create treeview for all borrowed books
    borrowed_table = ttk.Treeview(container, columns=("ID", "Book", "User", "Email", "Borrow_Date", "Due_Date", "Status"), show="headings", height=15)
    borrowed_table.heading("ID", text="Borrow ID")
    borrowed_table.heading("Book", text="Book Title")
    borrowed_table.heading("User", text="User Name")
    borrowed_table.heading("Email", text="Email")
    borrowed_table.heading("Borrow_Date", text="Borrow Date")
    borrowed_table.heading("Due_Date", text="Due Date")
    borrowed_table.heading("Status", text="Status")
    borrowed_table.pack(fill="both", expand=True, padx=10, pady=10)

    def refresh_borrowed_table():
        for item in borrowed_table.get_children():
            borrowed_table.delete(item)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("""
                SELECT br.borrow_id, b.title, u.full_name, u.email, br.borrow_date, br.due_date,
                       CASE WHEN br.return_date IS NULL THEN 'Borrowed' ELSE 'Returned' END as status
                FROM borrowed br
                JOIN books b ON br.book_id = b.book_id
                JOIN users u ON br.user_id = u.user_id
                ORDER BY br.borrow_date DESC
            """)
            
            for row in cur.fetchall():
                borrowed_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    refresh_borrowed_table()

    # Action buttons
    button_frame = tk.Frame(container, bg='white')
    button_frame.pack(pady=10)

    def return_book():
        selected = borrowed_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a borrowed book")
            return
        
        borrow_id = borrowed_table.item(selected)["values"][0]
        status = borrowed_table.item(selected)["values"][6]
        
        if status == "Returned":
            messagebox.showinfo("Info", "Book is already returned")
            return
        
        if messagebox.askyesno("Confirm Return", "Mark this book as returned?"):
            try:
                db = db_connection()
                cur = db.cursor()
                # Update return date and increment available copies
                cur.execute("UPDATE borrowed SET return_date = CURDATE() WHERE borrow_id = %s", (borrow_id,))
                cur.execute("""
                    UPDATE books SET available_copies = available_copies + 1 
                    WHERE book_id = (SELECT book_id FROM borrowed WHERE borrow_id = %s)
                """, (borrow_id,))
                db.commit()
                messagebox.showinfo("Success", "Book returned successfully")
                refresh_borrowed_table()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                db.close()

    tk.Button(button_frame, text="Mark as Returned", command=return_book, bg='lightgreen').pack(side="left", padx=5)
    tk.Button(button_frame, text="Back to Dashboard", command=lambda: navigate_to(admin_dashboard), bg='lightgray').pack(side="left", padx=5)

# ADMIN VIEW USER BORROWED BOOKS
def admin_user_borrowed():
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    tk.Label(container, text="User Borrowed Books", font=("Arial", 16, "bold"), bg='white').pack(pady=10)

    # User selection frame
    selection_frame = tk.Frame(container, bg='white')
    selection_frame.pack(pady=10)

    tk.Label(selection_frame, text="Select User:", bg='white').pack(side="left", padx=5)
    
    # Get all users
    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("SELECT user_id, full_name, email FROM users WHERE role='user'")
        users = cur.fetchall()
        user_options = [f"{user[1]} ({user[2]})" for user in users]
        db.close()
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        users = []
        user_options = []

    selected_user_var = tk.StringVar()
    user_combo = ttk.Combobox(selection_frame, textvariable=selected_user_var, values=user_options, width=40)
    user_combo.pack(side="left", padx=5)

    # Create treeview for user borrowed books
    borrowed_table = ttk.Treeview(container, columns=("ID", "Book", "Author", "Borrow_Date", "Due_Date", "Status"), show="headings", height=12)
    borrowed_table.heading("ID", text="Borrow ID")
    borrowed_table.heading("Book", text="Book Title")
    borrowed_table.heading("Author", text="Author")
    borrowed_table.heading("Borrow_Date", text="Borrow Date")
    borrowed_table.heading("Due_Date", text="Due Date")
    borrowed_table.heading("Status", text="Status")
    borrowed_table.pack(fill="both", expand=True, padx=10, pady=10)

    def load_user_books():
        selected_user = selected_user_var.get()
        if not selected_user:
            messagebox.showerror("Error", "Please select a user")
            return
        
        # Find user_id from the selection
        user_id = None
        for user in users:
            if f"{user[1]} ({user[2]})" == selected_user:
                user_id = user[0]
                break
        
        if not user_id:
            messagebox.showerror("Error", "Invalid user selection")
            return

        # Clear existing data
        for item in borrowed_table.get_children():
            borrowed_table.delete(item)

        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("""
                SELECT br.borrow_id, b.title, b.author, br.borrow_date, br.due_date,
                       CASE WHEN br.return_date IS NULL THEN 'Borrowed' ELSE 'Returned' END as status
                FROM borrowed br
                JOIN books b ON br.book_id = b.book_id
                WHERE br.user_id = %s
                ORDER BY br.borrow_date DESC
            """, (user_id,))
            
            for row in cur.fetchall():
                borrowed_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    tk.Button(selection_frame, text="Load Books", command=load_user_books, bg='lightblue').pack(side="left", padx=5)

    # Navigation buttons
    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=10)
    tk.Button(nav_frame, text="Back to Dashboard", command=lambda: navigate_to(admin_dashboard), bg='lightgray').pack()

# USER DASHBOARD - FIXED TO ONLY SHOW AVAILABLE BOOKS FOR BORROWING
def user_dashboard(user_id):
    for widget in window.winfo_children():
        widget.destroy()
    
    set_background_image(window)
    
    container = tk.Frame(window, bg='white', relief='raised', bd=2)
    container.pack(fill='both', expand=True, padx=10, pady=10)

    # Get user info
    try:
        db = db_connection()
        cur = db.cursor()
        cur.execute("SELECT full_name FROM users WHERE user_id=%s", (user_id,))
        user_name = cur.fetchone()[0]
        db.close()
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        user_name = "User"

    tk.Label(container, text=f"Welcome {user_name}", font=("Arial", 16, "bold"), bg='white').pack(pady=10)

    # Create notebook for tabs
    notebook = ttk.Notebook(container)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Available Books tab
    books_frame = ttk.Frame(notebook)
    notebook.add(books_frame, text="Available Books")

    # My Books tab
    my_books_frame = ttk.Frame(notebook)
    notebook.add(my_books_frame, text="My Borrowed Books")

    # AVAILABLE BOOKS TAB - USERS ONLY SEE BOOKS WITH COPIES AVAILABLE
    tk.Label(books_frame, text="Available Books", font=("Arial", 14, "bold")).pack(pady=5)
    
    # Search frame
    search_frame = tk.Frame(books_frame)
    search_frame.pack(pady=5)
    
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=5)
    
    search_by_var = tk.StringVar(value="Title")
    search_combo = ttk.Combobox(search_frame, textvariable=search_by_var, values=["Title", "Author", "Category"], width=10)
    search_combo.pack(side="left", padx=5)

    available_books_table = ttk.Treeview(books_frame, columns=("ID", "Title", "Author", "Category", "Available"), show="headings", height=12)
    available_books_table.heading("ID", text="Book ID")
    available_books_table.heading("Title", text="Title")
    available_books_table.heading("Author", text="Author")
    available_books_table.heading("Category", text="Category")
    available_books_table.heading("Available", text="Available Copies")
    available_books_table.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_available_books(search_term="", search_by="Title"):
        for item in available_books_table.get_children():
            available_books_table.delete(item)
        try:
            db = db_connection()
            cur = db.cursor()
            
            # Users only see books with available copies > 0
            if search_term:
                if search_by == "Title":
                    cur.execute("""
                        SELECT b.book_id, b.title, b.author, c.category_name, b.available_copies
                        FROM books b
                        JOIN categories c ON b.category_id = c.category_id
                        WHERE b.available_copies > 0 AND b.title LIKE %s
                        ORDER BY b.title
                    """, (f"%{search_term}%",))
                elif search_by == "Author":
                    cur.execute("""
                        SELECT b.book_id, b.title, b.author, c.category_name, b.available_copies
                        FROM books b
                        JOIN categories c ON b.category_id = c.category_id
                        WHERE b.available_copies > 0 AND b.author LIKE %s
                        ORDER BY b.title
                    """, (f"%{search_term}%",))
                else:  # Category
                    cur.execute("""
                        SELECT b.book_id, b.title, b.author, c.category_name, b.available_copies
                        FROM books b
                        JOIN categories c ON b.category_id = c.category_id
                        WHERE b.available_copies > 0 AND c.category_name LIKE %s
                        ORDER BY b.title
                    """, (f"%{search_term}%",))
            else:
                cur.execute("""
                    SELECT b.book_id, b.title, b.author, c.category_name, b.available_copies
                    FROM books b
                    JOIN categories c ON b.category_id = c.category_id
                    WHERE b.available_copies > 0
                    ORDER BY b.title
                """)
            
            for row in cur.fetchall():
                available_books_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    def search_books():
        search_term = search_entry.get().strip()
        search_by = search_by_var.get()
        refresh_available_books(search_term, search_by)

    tk.Button(search_frame, text="Search", command=search_books, bg='lightblue').pack(side="left", padx=5)
    tk.Button(search_frame, text="Show All", command=lambda: refresh_available_books(), bg='lightgray').pack(side="left", padx=5)

    refresh_available_books()

    # Book action buttons
    book_action_frame = tk.Frame(books_frame)
    book_action_frame.pack(pady=10)

    def borrow_book():
        selected = available_books_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book to borrow")
            return
        
        book_id = available_books_table.item(selected)["values"][0]
        book_title = available_books_table.item(selected)["values"][1]
        available_copies = available_books_table.item(selected)["values"][4]
        
        if available_copies <= 0:
            messagebox.showerror("Error", "No copies available")
            return
        
        if messagebox.askyesno("Confirm Borrow", f"Do you want to borrow '{book_title}'?"):
            try:
                db = db_connection()
                cur = db.cursor()
                
                # Check if user already has this book
                cur.execute("SELECT COUNT(*) FROM borrowed WHERE user_id=%s AND book_id=%s AND return_date IS NULL", (user_id, book_id))
                if cur.fetchone()[0] > 0:
                    messagebox.showerror("Error", "You already have this book borrowed")
                    return
                
                # Borrow the book (due date is 14 days from now)
                cur.execute("""
                    INSERT INTO borrowed (user_id, book_id, borrow_date, due_date) 
                    VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY))
                """, (user_id, book_id))
                
                # Decrease available copies
                cur.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))
                
                db.commit()
                messagebox.showinfo("Success", f"'{book_title}' borrowed successfully! Due date: 14 days from today.")
                refresh_available_books()
                refresh_my_books()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                db.close()

    tk.Button(book_action_frame, text="Borrow Book", command=borrow_book, bg='lightgreen').pack(side="left", padx=5)

    # MY BORROWED BOOKS TAB
    tk.Label(my_books_frame, text="My Borrowed Books", font=("Arial", 14, "bold")).pack(pady=5)
    
    my_books_table = ttk.Treeview(my_books_frame, columns=("ID", "Title", "Author", "Borrow_Date", "Due_Date", "Status"), show="headings", height=12)
    my_books_table.heading("ID", text="Borrow ID")
    my_books_table.heading("Title", text="Book Title")
    my_books_table.heading("Author", text="Author")
    my_books_table.heading("Borrow_Date", text="Borrow Date")
    my_books_table.heading("Due_Date", text="Due Date")
    my_books_table.heading("Status", text="Status")
    my_books_table.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh_my_books():
        for item in my_books_table.get_children():
            my_books_table.delete(item)
        try:
            db = db_connection()
            cur = db.cursor()
            cur.execute("""
                SELECT br.borrow_id, b.title, b.author, br.borrow_date, br.due_date,
                       CASE 
                           WHEN br.return_date IS NOT NULL THEN 'Returned'
                           WHEN br.due_date < CURDATE() THEN 'Overdue'
                           ELSE 'Borrowed'
                       END as status
                FROM borrowed br
                JOIN books b ON br.book_id = b.book_id
                WHERE br.user_id = %s
                ORDER BY br.borrow_date DESC
            """, (user_id,))
            
            for row in cur.fetchall():
                my_books_table.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    refresh_my_books()

    # My books action buttons
    my_books_action_frame = tk.Frame(my_books_frame)
    my_books_action_frame.pack(pady=10)

    def return_book():
        selected = my_books_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book to return")
            return
        
        borrow_id = my_books_table.item(selected)["values"][0]
        book_title = my_books_table.item(selected)["values"][1]
        status = my_books_table.item(selected)["values"][5]
        
        if status == "Returned":
            messagebox.showinfo("Info", "Book is already returned")
            return
        
        if messagebox.askyesno("Confirm Return", f"Do you want to return '{book_title}'?"):
            try:
                db = db_connection()
                cur = db.cursor()
                
                # Update return date and increment available copies
                cur.execute("UPDATE borrowed SET return_date = CURDATE() WHERE borrow_id = %s", (borrow_id,))
                cur.execute("""
                    UPDATE books SET available_copies = available_copies + 1 
                    WHERE book_id = (SELECT book_id FROM borrowed WHERE borrow_id = %s)
                """, (borrow_id,))
                
                db.commit()
                messagebox.showinfo("Success", f"'{book_title}' returned successfully!")
                refresh_my_books()
                refresh_available_books()
            except Exception as e:
                messagebox.showerror("DB Error", str(e))
            finally:
                db.close()

    tk.Button(my_books_action_frame, text="Return Book", command=return_book, bg='lightcoral').pack(side="left", padx=5)

    # Navigation and logout buttons
    nav_frame = tk.Frame(container, bg='white')
    nav_frame.pack(pady=10)
    
    def logout():
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            navigate_to(show_main_menu)
    
    tk.Button(nav_frame, text="Logout", command=logout, bg='lightgray').pack()

# MAIN APPLICATION
if __name__ == "__main__":
    window = tk.Tk()
    window.title("Library Management System")
    window.geometry("1000x700")
    window.minsize(800, 600)
    
    # Bind window resize event
    window.bind("<Configure>", on_window_resize)
    
    # Start with main menu
    show_main_menu()
    
    # Start the application
    window.mainloop()

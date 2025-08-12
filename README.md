# Library Management System
A comprehensive desktop application built with Python and Tkinter for managing library operations, including book inventory management, user administration, and book borrowing/returning workflows.
Features
Admin Capabilities
Book Management: Add, edit, and delete books from the library inventory
User Administration: Create, modify, and remove user accounts with role-based access
Borrowing Oversight: Monitor all borrowed books and track borrowing history
Analytics: View comprehensive reports on book availability and user activity

User Capabilities

Book Discovery: Browse available books in the library catalog
Borrowing System: Borrow available books with automatic inventory updates
Return Management: Return borrowed books with date tracking
Personal History: View complete borrowing history and currently held books

Technical Architecture
Core Technologies

GUI Framework: Tkinter with ttk for enhanced styling
Database: MySQL for persistent data storage
Security: SHA-256 password encryption
Image Processing: PIL (Python Imaging Library) for background image handling

Database Schema
The application utilizes three primary database tables:

users: Stores user credentials and role assignments
books: Maintains book inventory with availability tracking
borrowed: Records all borrowing transactions with timestamps

Installation Requirements
Prerequisites
Install the following Python packages using pip:
bashpip install mysql-connector-python
pip install pillow
Database Configuration

Install and configure MySQL server on your local machine
Create a database named library_system
Update database connection parameters in the db_connection() function if necessary
Ensure the MySQL service is running before launching the application

Application Setup

Clone or download the source code to your local directory
Place a background image file named library.png in the specified path or update the image path in the set_background_image() function
Execute the Python script to launch the application

Usage Instructions
Initial Setup
Upon first launch, register administrative users through the registration interface. The system supports role-based authentication with separate login processes for administrators and regular users.
Administrative Operations
Administrators access a comprehensive dashboard featuring tabbed interfaces for book management and user administration. The system provides complete CRUD operations for both books and users, with built-in validation to prevent data integrity issues.
User Operations
Regular users interact with a streamlined interface focused on book discovery and borrowing management. The system automatically handles inventory updates and maintains detailed transaction records.
Architecture Highlights
Navigation System
The application implements a sophisticated navigation system with history tracking, enabling users to navigate backward and forward through different screens seamlessly.
Dynamic Interface
The interface adapts to window resizing events, automatically adjusting the background image and maintaining visual consistency across different screen sizes.
Error Handling
Comprehensive error handling ensures graceful management of database connection issues, invalid user inputs, and system exceptions.
Security Implementation
User passwords undergo SHA-256 encryption before database storage, ensuring secure credential management throughout the application lifecycle.
Database Integration
The application maintains persistent connections to MySQL, implementing proper connection management with automatic cleanup procedures. All database operations include transaction management and error recovery mechanisms.
Customization Options
The system design supports straightforward customization of visual elements, including background images, color schemes, and layout configurations. Database connection parameters can be modified to accommodate different MySQL configurations or alternative database systems.
System Requirements

Python 3.x with Tkinter support
MySQL Server (local or remote installation)
Sufficient disk space for database storage and application files
Display resolution supporting minimum 800x600 window dimensions

This library management system provides a robust foundation for educational institutions, small libraries, or organizations requiring efficient book inventory management with user access controls.

Author : Sreejesh M S

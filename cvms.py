import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os

# Database Setup
def initialize_database():
    try:
        conn = sqlite3.connect("vaccination_system.db")
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                name TEXT,
                contact TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER,
                name TEXT,
                dob TEXT,
                FOREIGN KEY (parent_id) REFERENCES parents(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_id INTEGER,
                name TEXT,
                username TEXT UNIQUE,
                password TEXT,
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vaccines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age_months INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vaccine_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER,
                vaccine_id INTEGER,
                hospital_id INTEGER,
                health_worker_id INTEGER,
                date_administered TEXT,
                status TEXT,
                FOREIGN KEY (child_id) REFERENCES children(id),
                FOREIGN KEY (vaccine_id) REFERENCES vaccines(id),
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
                FOREIGN KEY (health_worker_id) REFERENCES health_workers(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vaccine_record_id INTEGER,
                amount REAL,
                status TEXT,
                date_paid TEXT,
                FOREIGN KEY (vaccine_record_id) REFERENCES vaccine_records(id)
            )
        """)
        
        # Insert sample vaccines
        cursor.execute("INSERT OR IGNORE INTO vaccines (name, age_months) VALUES ('DTP', 2)")
        cursor.execute("INSERT OR IGNORE INTO vaccines (name, age_months) VALUES ('Measles', 9)")
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
    finally:
        conn.close()

# Main Application Class
class VaccinationSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Child Vaccination Management System")
        self.root.geometry("800x600")
        try:
            initialize_database()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to start application: {str(e)}")
            return
        self.current_user = None
        self.user_role = None
        self.background_image = None
        self.show_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.background_image = None

    def set_background(self, image_name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "assets", image_name)
        try:
            img = Image.open(image_path)
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.background_image = tk.Label(self.root, image=self.photo)
            self.background_image.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Image file not found: {image_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def show_login_screen(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Child Vaccination Management System", font=("Arial", 16), bg="white").pack(pady=10)
        tk.Label(self.root, text="Login", font=("Arial", 14), bg="white").pack(pady=10)

        tk.Label(self.root, text="Role", bg="white").pack()
        self.role_var = tk.StringVar(value="Parent")
        tk.Radiobutton(self.root, text="Parent", variable=self.role_var, value="Parent", bg="white").pack()
        tk.Radiobutton(self.root, text="Hospital", variable=self.role_var, value="Hospital", bg="white").pack()
        tk.Radiobutton(self.root, text="Health Worker", variable=self.role_var, value="HealthWorker", bg="white").pack()

        tk.Label(self.root, text="Username", bg="white").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password", bg="white").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self.root, text="Register (Parent/Hospital)", command=self.show_register_screen, bg="#4a90e2", fg="white").pack()

    def show_register_screen(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Register", font=("Arial", 14), bg="white").pack(pady=10)

        tk.Label(self.root, text="Role", bg="white").pack()
        self.reg_role_var = tk.StringVar(value="Parent")
        tk.Radiobutton(self.root, text="Parent", variable=self.reg_role_var, value="Parent", bg="white").pack()
        tk.Radiobutton(self.root, text="Hospital", variable=self.reg_role_var, value="Hospital", bg="white").pack()

        tk.Label(self.root, text="Username", bg="white").pack()
        self.reg_username_entry = tk.Entry(self.root)
        self.reg_username_entry.pack()

        tk.Label(self.root, text="Password", bg="white").pack()
        self.reg_password_entry = tk.Entry(self.root, show="*")
        self.reg_password_entry.pack()

        tk.Label(self.root, text="Name", bg="white").pack()
        self.reg_name_entry = tk.Entry(self.root)
        self.reg_name_entry.pack()

        tk.Label(self.root, text="Contact (for Parents only)", bg="white").pack()
        self.reg_contact_entry = tk.Entry(self.root)
        self.reg_contact_entry.pack()

        tk.Button(self.root, text="Register", command=self.register, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.show_login_screen, bg="#4a90e2", fg="white").pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        try:
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            table = {"Parent": "parents", "Hospital": "hospitals", "HealthWorker": "health_workers"}[role]
            cursor.execute(f"SELECT * FROM {table} WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                self.current_user = user
                self.user_role = role
                if role == "Parent":
                    self.show_parent_dashboard()
                elif role == "Hospital":
                    self.show_hospital_dashboard()
                else:
                    self.show_health_worker_dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Login failed: {str(e)}")

    def register(self):
        role = self.reg_role_var.get()
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        name = self.reg_name_entry.get()
        contact = self.reg_contact_entry.get() if role == "Parent" else None

        try:
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            if role == "Parent":
                cursor.execute("INSERT INTO parents (username, password, name, contact) VALUES (?, ?, ?, ?)",
                               (username, password, name, contact))
            else:  # Hospital
                cursor.execute("INSERT INTO hospitals (username, password, name) VALUES (?, ?, ?)",
                               (username, password, name))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Registration failed: {str(e)}")
        finally:
            conn.close()

    def show_parent_dashboard(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text=f"Welcome, {self.current_user[3]} (Parent)", font=("Arial", 14), bg="white").pack(pady=10)

        tk.Button(self.root, text="Add Child", command=self.add_child, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(self.root, text="View Children & Book Appointment", command=self.view_children, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(self.root, text="View Appointments & Pay", command=self.view_appointments, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(self.root, text="View Reminders", command=self.view_reminders, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.show_login_screen, bg="#4a90e2", fg="white").pack(pady=5)

    def add_child(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Add Child", font=("Arial", 14), bg="white").pack(pady=10)

        tk.Label(self.root, text="Child Name", bg="white").pack()
        self.child_name_entry = tk.Entry(self.root)
        self.child_name_entry.pack()

        tk.Label(self.root, text="Date of Birth (YYYY-MM-DD)", bg="white").pack()
        self.dob_entry = tk.Entry(self.root)
        self.dob_entry.pack()

        tk.Button(self.root, text="Add Child", command=self.save_child, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_parent_dashboard, bg="#4a90e2", fg="white").pack()

    def save_child(self):
        name = self.child_name_entry.get()
        dob = self.dob_entry.get()
        parent_id = self.current_user[0]

        try:
            datetime.strptime(dob, "%Y-%m-%d")
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO children (parent_id, name, dob) VALUES (?, ?, ?)",
                           (parent_id, name, dob))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Child added successfully")
            self.show_parent_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format (use YYYY-MM-DD)")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add child: {str(e)}")

    def view_children(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Your Children", font=("Arial", 14), bg="white").pack(pady=10)

        try:
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM children WHERE parent_id = ?", (self.current_user[0],))
            children = cursor.fetchall()

            tree = ttk.Treeview(self.root, columns=("ID", "Name", "DOB"), show="headings")
            tree.heading("ID", text="Child ID")
            tree.heading("Name", text="Name")
            tree.heading("DOB", text="Date of Birth")
            tree.pack(pady=10)

            for child in children:
                tree.insert("", tk.END, values=child)

            tk.Label(self.root, text="Enter Child ID to Book Appointment", bg="white").pack()
            self.child_id_entry = tk.Entry(self.root)
            self.child_id_entry.pack()

            tk.Label(self.root, text="Select Vaccine", bg="white").pack()
            cursor.execute("SELECT id, name FROM vaccines")
            vaccines = cursor.fetchall()
            self.vaccine_var = tk.StringVar()
            tk.OptionMenu(self.root, self.vaccine_var, *[f"{v[1]} (ID: {v[0]})" for v in vaccines]).pack()

            tk.Label(self.root, text="Select Hospital", bg="white").pack()
            cursor.execute("SELECT id, name FROM hospitals")
            hospitals = cursor.fetchall()
            self.hospital_var = tk.StringVar()
            tk.OptionMenu(self.root, self.hospital_var, *[f"{h[1]} (ID: {h[0]})" for h in hospitals]).pack()

            tk.Button(self.root, text="Book Appointment", command=self.book_appointment, bg="#4CAF50", fg="white").pack(pady=10)
            tk.Button(self.root, text="Back", command=self.show_parent_dashboard, bg="#4a90e2", fg="white").pack()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load children: {str(e)}")

    def book_appointment(self):
        child_id = self.child_id_entry.get()
        vaccine_selection = self.vaccine_var.get()
        hospital_selection = self.hospital_var.get()

        try:
            vaccine_id = int(vaccine_selection.split("ID: ")[1].strip(")"))
            hospital_id = int(hospital_selection.split("ID: ")[1].strip(")"))
            appointment_date = datetime.now().strftime("%Y-%m-%d")

            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vaccine_records (child_id, vaccine_id, hospital_id, date_administered, status) VALUES (?, ?, ?, ?, ?)",
                           (child_id, vaccine_id, hospital_id, appointment_date, "Scheduled"))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Appointment booked successfully")
            self.view_appointments()
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid selection")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to book appointment: {str(e)}")

    def view_appointments(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Your Appointments", font=("Arial", 14), bg="white").pack(pady=10)

        try:
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vr.id, c.name, v.name, h.name, vr.date_administered, vr.status, p.amount, p.status
                FROM vaccine_records vr
                JOIN children c ON vr.child_id = c.id
                JOIN vaccines v ON vr.vaccine_id = v.id
                JOIN hospitals h ON vr.hospital_id = h.id
                LEFT JOIN payments p ON vr.id = p.vaccine_record_id
                WHERE c.parent_id = ?
            """, (self.current_user[0],))
            appointments = cursor.fetchall()

            tree = ttk.Treeview(self.root, columns=("ID", "Child", "Vaccine", "Hospital", "Date", "Status", "Amount", "Payment Status"), show="headings")
            tree.heading("ID", text="Appointment ID")
            tree.heading("Child", text="Child")
            tree.heading("Vaccine", text="Vaccine")
            tree.heading("Hospital", text="Hospital")
            tree.heading("Date", text="Date")
            tree.heading("Status", text="Status")
            tree.heading("Amount", text="Amount")
            tree.heading("Payment Status", text="Payment Status")
            tree.pack(pady=10)

            for appt in appointments:
                amount = appt[6] if appt[6] else "50.00"
                payment_status = appt[7] if appt[7] else "Pending"
                tree.insert("", tk.END, values=(appt[0], appt[1], appt[2], appt[3], appt[4], appt[5], amount, payment_status))

            tk.Label(self.root, text="Enter Appointment ID to Pay", bg="white").pack()
            self.appt_id_entry = tk.Entry(self.root)
            self.appt_id_entry.pack()

            tk.Button(self.root, text="Pay Now", command=self.make_payment, bg="#4CAF50", fg="white").pack(pady=10)
            tk.Button(self.root, text="Back", command=self.show_parent_dashboard, bg="#4a90e2", fg="white").pack()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load appointments: {str(e)}")

    def make_payment(self):
        appt_id = self.appt_id_entry.get()
        try:
            appt_id = int(appt_id)
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payments WHERE vaccine_record_id = ?", (appt_id,))
            payment = cursor.fetchone()

            if payment:
                messagebox.showinfo("Info", "Payment already made")
            else:
                amount = 50.00
                date_paid = datetime.now().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO payments (vaccine_record_id, amount, status, date_paid) VALUES (?, ?, ?, ?)",
                               (appt_id, amount, "Paid", date_paid))
                conn.commit()
                messagebox.showinfo("Success", f"Payment of ${amount} successful")
            conn.close()
            self.view_appointments()
        except ValueError:
            messagebox.showerror("Error", "Invalid Appointment ID")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to process payment: {str(e)}")

    def view_reminders(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Reminders", font=("Arial", 14), bg="white").pack(pady=10)

        try:
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, dob FROM children WHERE parent_id = ?", (self.current_user[0],))
            children = cursor.fetchall()

            reminders = []
            today = datetime.now()
            for child in children:
                child_id, name, dob = child
                dob_date = datetime.strptime(dob, "%Y-%m-%d")
                age_months = (today - dob_date).days // 30
                cursor.execute("SELECT id, name, age_months FROM vaccines")
                vaccines = cursor.fetchall()
                for vaccine in vaccines:
                    v_id, v_name, v_age = vaccine
                    cursor.execute("SELECT * FROM vaccine_records WHERE child_id = ? AND vaccine_id = ?", (child_id, v_id))
                    if not cursor.fetchone() and age_months >= v_age:
                        reminders.append(f"{name} is due for {v_name} (Recommended at {v_age} months)")

            if reminders:
                for reminder in reminders:
                    tk.Label(self.root, text=reminder, fg="red", bg="white").pack()
            else:
                tk.Label(self.root, text="No reminders at this time", bg="white").pack()

            tk.Button(self.root, text="Back", command=self.show_parent_dashboard, bg="#4a90e2", fg="white").pack(pady=10)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load reminders: {str(e)}")

    def show_hospital_dashboard(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text=f"Welcome, {self.current_user[1]} (Hospital)", font=("Arial", 14), bg="white").pack(pady=10)

        tk.Button(self.root, text="View Appointments", command=self.hospital_view_appointments, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(self.root, text="Add Health Worker", command=self.add_health_worker, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.show_login_screen, bg="#4a90e2", fg="white").pack(pady=5)

    def hospital_view_appointments(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Hospital Appointments", font=("Arial", 14), bg="white").pack(pady=10)

        try:
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vr.id, c.name, v.name, vr.date_administered, vr.status
                FROM vaccine_records vr
                JOIN children c ON vr.child_id = c.id
                JOIN vaccines v ON vr.vaccine_id = v.id
                WHERE vr.hospital_id = ?
            """, (self.current_user[0],))
            appointments = cursor.fetchall()

            tree = ttk.Treeview(self.root, columns=("ID", "Child", "Vaccine", "Date", "Status"), show="headings")
            tree.heading("ID", text="Appointment ID")
            tree.heading("Child", text="Child")
            tree.heading("Vaccine", text="Vaccine")
            tree.heading("Date", text="Date")
            tree.heading("Status", text="Status")
            tree.pack(pady=10)

            for appt in appointments:
                tree.insert("", tk.END, values=appt)

            tk.Button(self.root, text="Back", command=self.show_hospital_dashboard, bg="#4a90e2", fg="white").pack(pady=10)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load appointments: {str(e)}")

    def add_health_worker(self):
        self.clear_screen()
        self.set_background("assets/vaccine1.jpg")
        tk.Label(self.root, text="Add Health Worker", font=("Arial", 14), bg="white").pack(pady=10)

        tk.Label(self.root, text="Health Worker Name", bg="white").pack()
        self.hw_name_entry = tk.Entry(self.root)
        self.hw_name_entry.pack()

        tk.Label(self.root, text="Username", bg="white").pack()
        self.hw_username_entry = tk.Entry(self.root)
        self.hw_username_entry.pack()

        tk.Label(self.root, text="Password", bg="white").pack()
        self.hw_password_entry = tk.Entry(self.root, show="*")
        self.hw_password_entry.pack()

        tk.Button(self.root, text="Add Health Worker", command=self.save_health_worker, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_hospital_dashboard, bg="#4a90e2", fg="white").pack()

    def save_health_worker(self):
        name = self.hw_name_entry.get()
        username = self.hw_username_entry.get()
        password = self.hw_password_entry.get()
        hospital_id = self.current_user[0]

        try:
            conn = sqlite3.connect("vaccination_system.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO health_workers (hospital_id, name, username, password) VALUES (?, ?, ?, ?)",
                           (hospital_id, name, username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Health Worker added successfully")
            self.show_hospital_dashboard()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
if __name__ == "__main__":
    root = tk.Tk()
app = VaccinationSystemApp(root)
root.mainloop()
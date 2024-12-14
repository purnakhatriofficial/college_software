import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import csv
import os
import json
import hashlib
from datetime import datetime
from PIL import Image, ImageTk

class AdmissionManagementSystem:
    def __init__(self, root, username):
        self.root = root
        self.current_user = username
        self.root.title(f"Nepal Rastray Secondary School - Admission System (User: {username})")
        self.root.geometry("1920x1080")

        # Ensure data directories exist
        self.ensure_data_directories()

        # Create GUI components
        self.create_widgets()

        # Selected photo path
        self.photo_path = None

    def ensure_data_directories(self):
        # Ensure directories exist
        os.makedirs('student_photos', exist_ok=True)
        
        # Ensure students CSV exists
        if not os.path.exists('students.csv'):
            with open('students.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Name', 'Email', 'Fathers Name', 'Blood Group', 
                                 'Course', 'Phone', 'Years', 'Address', 'Photo', 'Entry Date Time'])

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=10, fill='both', expand=True)

        # Left frame for inputs
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill='y', padx=10)

        # Input Fields
        fields = [
            ('Name', 0, 0), ('Email', 0, 2), 
            ('Fathers Name', 1, 0), ('Blood Group', 1, 2),
            ('Phone', 2, 0), ('Years', 2, 2),
            ('Address', 3, 0)
        ]

        self.entries = {}
        for label, row, col in fields:
            tk.Label(left_frame, font=("Arial", 12), text=label).grid(row=row, column=col, padx=5, pady=5, sticky='e')
            entry = tk.Entry(left_frame, font=("Arial", 12), width=20)
            entry.grid(row=row, column=col+1, padx=5, pady=5)
            self.entries[label] = entry

        # Course Dropdown
        tk.Label(left_frame, font=("Arial", 12), text="Course").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.course_var = tk.StringVar()
        courses = ['Web Development', 'App Development', 
                   'Digital Marketing', 'Graphics Design']
        course_dropdown = ttk.Combobox(left_frame, textvariable=self.course_var, 
                                        values=courses, font=("Arial", 12), width=20)
        course_dropdown.grid(row=4, column=1, padx=5, pady=5)

        # Photo Upload Section
        tk.Label(left_frame, font=("Arial", 12),  text="Student Photo").grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.photo_button = tk.Button(left_frame, font=("Arial", 12), width=15, cursor="hand2", bg="yellow", text="Upload Photo", command=self.upload_photo)
        self.photo_button.grid(row=5, column=1, padx=5, pady=5)

        # Photo Preview
        self.photo_label = tk.Label(left_frame, text="No photo selected")
        self.photo_label.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        # Buttons Frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, pady=10)

        buttons = [
            ("Add Student", self.add_student),
            ("View Students", self.view_students),
            ("Update Student", self.update_student),
            ("Delete Student", self.delete_student),
            ("Logout", self.logout)
        ]

        for text, command in buttons:
            tk.Button(button_frame, bg="#C2FBD7", width=15, cursor="hand2",  text=text, command=command).pack(side=tk.LEFT, padx=5)

    def upload_photo(self):
        # Open file dialog to select photo
        file_path = filedialog.askopenfilename(
            title="Select Student Photo", 
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        
        if file_path:
            # Resize and preview photo
            try:
                original_image = Image.open(file_path)
                # Resize to a standard size while maintaining aspect ratio
                original_image.thumbnail((200, 200))
                
                # Save a copy in student_photos directory
                filename = f"student_{self.generate_student_id()}.jpg"
                photo_save_path = os.path.join('student_photos', filename)
                original_image.save(photo_save_path)
                
                # Display preview
                photo = ImageTk.PhotoImage(original_image)
                self.photo_label.config(image=photo, text='')
                self.photo_label.image = photo  # Keep a reference
                
                # Store photo path
                self.photo_path = filename

            except Exception as e:
                messagebox.showerror("Photo Upload Error", str(e))

    def add_student(self):
        # Collect data from entries
        student_id = self.generate_student_id()
        data = [
            student_id,
            self.entries['Name'].get(),
            self.entries['Email'].get(),
            self.entries['Fathers Name'].get(),
            self.entries['Blood Group'].get(),
            self.course_var.get(),
            self.entries['Phone'].get(),
            self.entries['Years'].get(),
            self.entries['Address'].get(),
            self.photo_path if self.photo_path else '',  # Photo path
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        # Validate input
        if not all(data[1:5]):  # Ensure critical fields are not empty
            messagebox.showerror("Error", "Please fill all required fields")
            return

        # Save to CSV
        with open('students.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

        messagebox.showinfo("Success", f"Student added successfully! Student ID: {student_id}")
        self.clear_entries()

    def view_students(self):
        # Create a new window to display students
        view_window = tk.Toplevel(self.root)
        view_window.title("Student List")
        view_window.geometry("1000x600")

        # Create Treeview
        columns = ('ID', 'Name', 'Email', 'Course', 'Phone', 'Photo')
        tree = ttk.Treeview(view_window, columns=columns, show='headings')
        
        # Configure column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')

        # Read and populate data
        with open('students.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                # Display photo path or 'No Photo' if empty
                photo_display = row[9] if row[9] else 'No Photo'
                tree.insert('', 'end', values=(row[0], row[1], row[2], row[5], row[6], photo_display))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(view_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        # Double-click to view photo
        def show_photo(event):
            selected_item = tree.selection()
            if selected_item:
                item_details = tree.item(selected_item)
                photo_path = item_details['values'][5]
                
                if photo_path and photo_path != 'No Photo':
                    # Find full path of the photo
                    full_photo_path = os.path.join('student_photos', photo_path)
                    
                    # Open photo in a new window
                    photo_window = tk.Toplevel(view_window)
                    photo_window.title("Student Photo")
                    
                    # Load and display photo
                    photo = ImageTk.PhotoImage(Image.open(full_photo_path))
                    photo_label = tk.Label(photo_window, image=photo)
                    photo_label.image = photo  # Keep a reference
                    photo_label.pack()

        tree.bind('<Double-1>', show_photo)

        # Pack widgets
        tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

    def update_student(self):
        # Prompt for student ID to update
        student_id = simpledialog.askstring("Update Student", "Enter Student ID to update:")
        if not student_id:
            return

        # Read all students
        students = []
        updated = False
        with open('students.csv', 'r') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Read headers
            students = list(csv_reader)

        # Find and update student
        for student in students:
            if student[0] == student_id:
                # Update student details from current entries
                student[1] = self.entries['Name'].get() or student[1]
                student[2] = self.entries['Email'].get() or student[2]
                student[3] = self.entries['Fathers Name'].get() or student[3]
                student[4] = self.entries['Blood Group'].get() or student[4]
                student[5] = self.course_var.get() or student[5]
                student[6] = self.entries['Phone'].get() or student[6]
                student[7] = self.entries['Years'].get() or student[7]
                student[8] = self.entries['Address'].get() or student[8]
                
                # Update photo if a new one is selected
                if self.photo_path:
                    student[9] = self.photo_path
                
                updated = True
                break

        if updated:
            # Write back to CSV
            with open('students.csv', 'w', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(headers)
                csv_writer.writerows(students)
            
            messagebox.showinfo("Success", f"Student {student_id} updated successfully!")
            self.clear_entries()
        else:
            messagebox.showerror("Error", f"No student found with ID {student_id}")

    def delete_student(self):
        # Prompt for student ID to delete
        student_id = simpledialog.askstring("Delete Student", "Enter Student ID to delete:")
        if not student_id:
            return

        # Read all students
        students = []
        with open('students.csv', 'r') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Read headers
            students = list(csv_reader)

        # Filter out the student to delete
        original_count = len(students)
        students = [student for student in students if student[0] != student_id]

        # Check if any student was deleted
        if len(students) < original_count:
            # Write back to CSV
            with open('students.csv', 'w', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(headers)
                csv_writer.writerows(students)
            
            messagebox.showinfo("Success", f"Student {student_id} deleted successfully!")
        else:
            messagebox.showerror("Error", f"No student found with ID {student_id}")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.course_var.set('')
        self.photo_label.config(image='', text='No photo selected')
        self.photo_path = None

    def generate_student_id(self):
        # Read existing students to generate unique ID
        try:
            with open('students.csv', 'r') as file:
                lines = list(csv.reader(file))
                if len(lines) > 1:
                    last_id = int(lines[-1][0])
                    return str(last_id + 1)
                else:
                    return "1"
        except Exception:
            return "1"

    def logout(self):
        self.root.destroy()
        show_login_window()

class LoginSystem:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def load_users():
        try:
            with open('users.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # Create default admin user if no users exist
            default_users = {
                "admin": LoginSystem.hash_password("nepal123")
            }
            with open('users.json', 'w') as file:
                json.dump(default_users, file)
            return default_users

    @staticmethod
    def validate_login(username, password):
        users = LoginSystem.load_users()
        hashed_password = LoginSystem.hash_password(password)
        return users.get(username) == hashed_password

    @staticmethod
    def add_user(username, password):
        users = LoginSystem.load_users()
        users[username] = LoginSystem.hash_password(password)
        with open('users.json', 'w') as file:
            json.dump(users, file)

def show_login_window():
    # Create login window
    login_root = tk.Tk()
    login_root.title("Login - Admission System")
    login_root.geometry("500x400")

    # Username
    tk.Label(login_root,  font="20", text="Username:").pack(pady=(20,5))
    username_entry = tk.Entry(login_root, font="20", width=15)
    username_entry.pack(pady=5)

    # Password
    tk.Label(login_root, font="20", text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_root, show="*", width=15, font="20")
    password_entry.pack(pady=5)

    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()

        if LoginSystem.validate_login(username, password):
            login_root.destroy()
            root = tk.Tk()
            AdmissionManagementSystem(root, username)
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    # Login Button
    tk.Button(login_root, bg="#4681f4", width=12, border=2, cursor="hand2", font=("Arial", 12), text="Login", command=attempt_login).pack(pady=10)

    # Register Button
    def open_register_window():
        reg_window = tk.Toplevel(login_root)
        reg_window.title("Register New User")
        reg_window.geometry("500x400")

        tk.Label(reg_window, font=("Arial", 20), text="New Username:").pack(pady=(20,5))
        new_username = tk.Entry(reg_window,  font=("Arial", 20), width=15)
        new_username.pack(pady=5)

        tk.Label(reg_window, font=("Arial", 20), text="New Password:").pack(pady=5)
        new_password = tk.Entry(reg_window,  font=
            ("Arial", 20), show="*", width=15)
        new_password.pack(pady=5)

        def register():
            username = new_username.get()
            password = new_password.get()
            
            if username and password:
                LoginSystem.add_user(username, password)
                messagebox.showinfo("Success", "User registered successfully!")
                reg_window.destroy()
            else:
                messagebox.showerror("Error", "Username and password cannot be empty")

        tk.Button(reg_window, bg="#4681f4", cursor="hand2", width=15, font=("Arial", 12), text="Register", command=register).pack(pady=10)

    tk.Button(login_root, bg="pink", cursor="hand2", width=18, font=("Arial", 12), text="Register New User", command=open_register_window).pack(pady=5)

    login_root.mainloop()

# Main execution
if __name__ == "__main__":
    show_login_window()


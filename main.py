import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import csv
import os
import shutil
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches

# Helper function to get file paths in user_data directory
def get_data_file_path(filename):
    """Get the full path for a data file in the user_data directory"""
    user_data_dir = "user_data"
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return os.path.join(user_data_dir, filename)

# Backup functionality
def get_backup_dir():
    """Get the backup directory path"""
    return r"c:\Users\Mert\Documents\GurgenBudgetTracker"

def get_last_backup_time():
    """Get the timestamp of the last backup"""
    backup_log_file = "backup_log.json"
    try:
        if os.path.exists(backup_log_file):
            with open(backup_log_file, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get('last_backup', '1970-01-01T00:00:00'))
    except:
        pass
    return datetime(1970, 1, 1)  # Very old date if no backup log exists

def save_backup_time():
    """Save the current time as the last backup time"""
    backup_log_file = "backup_log.json"
    try:
        data = {'last_backup': datetime.now().isoformat()}
        with open(backup_log_file, 'w') as f:
            json.dump(data, f)
    except:
        pass  # Fail silently if we can't save backup log

def should_backup():
    """Check if we should perform a backup (once per hour)"""
    last_backup = get_last_backup_time()
    current_time = datetime.now()
    time_diff = current_time - last_backup
    return time_diff >= timedelta(hours=1)

def backup_user_data():
    """Backup the user_data folder to Documents directory with timestamped folder"""
    if not should_backup():
        return False
    
    try:
        source_dir = "user_data"
        base_backup_dir = get_backup_dir()
        
        # Create timestamped folder name
        current_time = datetime.now()
        timestamp = current_time.strftime("%d_%m_%Y_%H%M")
        folder_name = f"user_data({timestamp})"
        timestamped_backup_dir = os.path.join(base_backup_dir, folder_name)
        
        # Create base backup directory if it doesn't exist
        if not os.path.exists(base_backup_dir):
            os.makedirs(base_backup_dir)
        
        # Create timestamped backup directory
        if not os.path.exists(timestamped_backup_dir):
            os.makedirs(timestamped_backup_dir)
        
        # Copy all files from user_data to timestamped backup directory
        if os.path.exists(source_dir):
            for filename in os.listdir(source_dir):
                source_file = os.path.join(source_dir, filename)
                dest_file = os.path.join(timestamped_backup_dir, filename)
                
                if os.path.isfile(source_file):
                    shutil.copy2(source_file, dest_file)
        
        # Save backup timestamp
        save_backup_time()
        print(f"Backup saved to: {timestamped_backup_dir}")
        return True
        
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

class BudgetTrackerApp(ThemedTk):
    def __init__(self):
        super().__init__()

        self.set_theme("clam")

        self.title("Gurgen Budget Tracker")
        self.geometry("800x600")

        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left toolbar
        self.toolbar = ttk.Frame(main_container, width=200)
        self.toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # Right main area
        self.main_area = ttk.Frame(main_container)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        self.pages = {}

        # Create and pack the pages
        for PageClass in (Dashboard, Transactions, LabelsAndTypes, Analytics, Settings):
            page = PageClass(self.main_area, self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Add buttons to the toolbar
        toolbar_label = ttk.Label(self.toolbar, text="Menu", font=("Arial", 16))
        toolbar_label.pack(pady=10)

        buttons = [
            ("Dashboard", "Dashboard"),
            ("Transactions", "Transactions"),
            ("Labels & Types", "LabelsAndTypes"),
            ("Analytics", "Analytics"),
            ("Settings", "Settings")
        ]

        for text, page_name in buttons:
            button = ttk.Button(self.toolbar, text=text, command=lambda p=page_name: self.show_page(p))
            button.pack(fill=tk.X, padx=5, pady=2)

        self.show_page("Dashboard")
        
        # Perform automatic backup on startup (once per hour)
        self.perform_startup_backup()

    def perform_startup_backup(self):
        """Perform backup if it's been more than an hour since last backup"""
        try:
            if backup_user_data():
                print("Backup completed successfully")
            else:
                print("Backup skipped (too recent)")
        except Exception as e:
            print(f"Backup error: {e}")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()
        
        # Refresh dashboard balance when navigating to it
        if page_name == "Dashboard" and hasattr(page, 'update_balance'):
            page.update_balance()

class Page(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

class Dashboard(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        
        # Main title
        title_label = ttk.Label(self, text="Dashboard", font=("Arial", 24))
        title_label.pack(pady=(20, 10))
        
        # Current Balance Section
        self.create_balance_section()
        
        # Load and display balance
        self.update_balance()
    
    def create_balance_section(self):
        """Create the current balance display section"""
        # Balance frame
        balance_frame = ttk.Frame(self)
        balance_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Balance label
        balance_title = ttk.Label(balance_frame, text="Current Balance", 
                                font=("Arial", 18, "bold"))
        balance_title.pack(pady=(0, 10))
        
        # Balance amount (big and prominent)
        self.balance_label = ttk.Label(balance_frame, text="₺0.00", 
                                     font=("Arial", 48, "bold"))
        self.balance_label.pack(pady=10)
        
        # Separator line
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=20)
    
    def update_balance(self):
        """Update the balance display with current data"""
        # Calculate total balance from all transactions
        total_expenses, total_income = self.calculate_all_time_totals()
        current_balance = total_income - total_expenses
        
        # Update balance label
        self.balance_label.config(text=f"₺{current_balance:.2f}")
        
        # Set color based on positive/negative balance
        if current_balance >= 0:
            self.balance_label.config(foreground="darkgreen")
        else:
            self.balance_label.config(foreground="darkred")
    
    def calculate_all_time_totals(self):
        """Calculate total expenses and income from all transactions"""
        total_expenses = 0.0
        total_income = 0.0
        
        try:
            with open(get_data_file_path("transactions_database.csv"), 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                
                for row in reader:
                    if row and len(row) >= 5:
                        try:
                            flow_type = row[0]
                            amount = float(row[2])
                            
                            if flow_type == "Expense":
                                total_expenses += amount
                            elif flow_type == "Income":
                                total_income += amount
                        except (ValueError, IndexError):
                            continue  # Skip invalid transactions
        except FileNotFoundError:
            pass  # No transactions file yet
        
        return total_expenses, total_income

class Transactions(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        
        label = ttk.Label(self, text="Transactions Page", font=("Arial", 24))
        label.pack(pady=20, padx=20)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        add_expense_btn = ttk.Button(button_frame, text="Add Expense", command=lambda: self.add_transaction("Expense"))
        add_expense_btn.pack(side=tk.LEFT, padx=10)

        add_income_btn = ttk.Button(button_frame, text="Add Income", command=lambda: self.add_transaction("Income"))
        add_income_btn.pack(side=tk.LEFT, padx=10)

        delete_transaction_btn = ttk.Button(button_frame, text="Delete Transaction", command=self.delete_transaction)
        delete_transaction_btn.pack(side=tk.LEFT, padx=10)

        # Create transactions display area
        transactions_frame = ttk.Frame(self)
        transactions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Transactions list - using Text widget for better control
        self.transactions_text = tk.Text(transactions_frame, font=("Arial", 10), wrap=tk.WORD, cursor="hand2")
        self.transactions_text.pack(fill=tk.BOTH, expand=True, padx=(20, 5), pady=5)

        # Configure tags for formatting
        self.transactions_text.tag_configure("expense", foreground="red")
        self.transactions_text.tag_configure("income", foreground="green")
        self.transactions_text.tag_configure("date", foreground="gray", font=("Arial", 9))
        self.transactions_text.tag_configure("amount", font=("Arial", 10, "bold"))
        self.transactions_text.tag_configure("selected", background="lightblue")

        # Store selection tracking
        self.transactions_text.selected_line = None
        self.selected_transaction_index = None
        
        # Bind click events for selection - try multiple event types
        self.transactions_text.bind("<Button-1>", self.on_transaction_click)
        self.transactions_text.bind("<ButtonRelease-1>", self.on_transaction_click)
        
        # Make text widget read-only but allow selection
        self.transactions_text.bind("<Key>", lambda e: "break")  # Prevent typing

        # Load and display existing transactions
        self.load_transactions()

    def add_transaction(self, flow_type):
        """Add a new transaction (expense or income)"""
        # Determine which labels file to use
        if flow_type == "Expense":
            labels_file = get_data_file_path("expense_labels.csv")
        else:
            labels_file = get_data_file_path("income_labels.csv")

        # Load available labels
        available_labels = []
        label_to_type = {}
        
        try:
            with open(labels_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 3:
                        type_name = row[0]
                        label_name = row[1]
                        available_labels.append(label_name)
                        label_to_type[label_name] = type_name
        except FileNotFoundError:
            tk.messagebox.showwarning("No Labels", f"Please create some {flow_type.lower()} labels first.")
            return

        if not available_labels:
            tk.messagebox.showwarning("No Labels", f"Please create some {flow_type.lower()} labels first.")
            return

        # Show transaction dialog
        result = self.show_transaction_dialog(flow_type, available_labels)
        if not result:
            return

        label_name, amount = result
        type_name = label_to_type[label_name]

        # Get current date
        from datetime import datetime
        current_date = datetime.now().strftime("%d/%m/%Y")

        # Save to CSV
        try:
            # Check if file exists and ends with newline
            file_needs_newline = False
            try:
                with open(get_data_file_path("transactions_database.csv"), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content and not content.endswith('\n'):
                        file_needs_newline = True
            except FileNotFoundError:
                pass
            
            # Add newline if needed
            if file_needs_newline:
                with open(get_data_file_path("transactions_database.csv"), 'a', encoding='utf-8') as f:
                    f.write('\n')
            
            # Now append the new transaction
            with open(get_data_file_path("transactions_database.csv"), 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([flow_type, label_name, amount, type_name, current_date])
            
            # Update usage counts for label and type
            self.update_usage_counts(flow_type, label_name, type_name)
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error saving transaction: {e}")
            return

        # Reload transactions display
        self.load_transactions()

    def show_transaction_dialog(self, flow_type, available_labels):
        """Show dialog for entering transaction details"""
        dialog = tk.Toplevel()
        dialog.title(f"Add {flow_type}")
        dialog.geometry("400x350")
        dialog.transient()
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"400x350+{x}+{y}")

        result = {'label': None, 'amount': None}

        # Label selection
        ttk.Label(dialog, text="Select Label:", font=("Arial", 12)).pack(pady=5)
        
        label_listbox = tk.Listbox(dialog, selectmode=tk.SINGLE, height=8)
        label_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for label in available_labels:
            label_listbox.insert(tk.END, label)

        # Amount input
        ttk.Label(dialog, text="Amount (₺):", font=("Arial", 12)).pack(pady=(15, 5))
        amount_entry = ttk.Entry(dialog, width=20, font=("Arial", 12))
        amount_entry.pack(pady=5)
        amount_entry.focus()

        def on_ok():
            selection = label_listbox.curselection()
            amount_text = amount_entry.get().strip()

            if not selection:
                tk.messagebox.showwarning("Missing Label", "Please select a label.")
                return

            if not amount_text:
                tk.messagebox.showwarning("Missing Amount", "Please enter an amount.")
                return

            try:
                # Validate amount is a number
                amount = float(amount_text)
                if amount <= 0:
                    tk.messagebox.showwarning("Invalid Amount", "Amount must be greater than 0.")
                    return
            except ValueError:
                tk.messagebox.showwarning("Invalid Amount", "Please enter a valid number.")
                return

            result['label'] = available_labels[selection[0]]
            result['amount'] = amount
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)

        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)

        # Bind Enter key to OK
        dialog.bind('<Return>', lambda e: on_ok())

        # Wait for dialog to close
        dialog.wait_window()

        if result['label'] and result['amount']:
            return (result['label'], result['amount'])
        return None

    def load_transactions(self):
        """Load and display transactions from CSV"""
        self.transactions_text.delete("1.0", tk.END)

        try:
            transactions = []
            with open(get_data_file_path("transactions_database.csv"), 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if row and len(row) >= 5:
                        transactions.append(row)

            # Simply reverse the list so newest (last added) appears first
            transactions.reverse()

            if not transactions:
                # Add top padding with empty lines
                self.transactions_text.insert(tk.END, "\n\n")
                self.transactions_text.insert(tk.END, "    No transactions yet. Add your first transaction using the buttons above!")
            else:
                # Add top padding with empty lines
                self.transactions_text.insert(tk.END, "\n")
                
                for i, (flow, label, amount, type_name, date) in enumerate(transactions):
                    if i > 0:
                        self.transactions_text.insert(tk.END, "\n")
                    
                    # Add left padding with spaces and format: "Date - Label (Type) - ₺Amount [Flow]"
                    self.transactions_text.insert(tk.END, "    ")  # Left padding
                    self.transactions_text.insert(tk.END, f"{date}", "date")
                    self.transactions_text.insert(tk.END, f" - {label} ({type_name}) - ")
                    self.transactions_text.insert(tk.END, f"₺{amount}", "amount")
                    
                    flow_tag = "expense" if flow == "Expense" else "income"
                    flow_symbol = " [-]" if flow == "Expense" else " [+]"
                    self.transactions_text.insert(tk.END, flow_symbol, flow_tag)
                    self.transactions_text.insert(tk.END, "\n")

        except FileNotFoundError:
            # Add top padding with empty lines
            self.transactions_text.insert(tk.END, "\n\n")
            self.transactions_text.insert(tk.END, "    No transactions yet. Add your first transaction using the buttons above!")
        except Exception as e:
            self.transactions_text.insert(tk.END, f"    Error loading transactions: {e}")

        # Reset selection
        self.transactions_text.selected_line = None
        self.selected_transaction_index = None

    def on_transaction_click(self, event):
        """Handle clicks on transaction text for selection."""
        print("Click event fired!")  # Debug print
        
        # Clear previous selection
        self.transactions_text.tag_remove("selected", "1.0", tk.END)
        
        # Get the line number where clicked
        index = self.transactions_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        
        print(f"Clicked on line {line_num}")  # Debug print
        
        # Get the content of the line
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_content = self.transactions_text.get(line_start, line_end)
        
        print(f"Line content: '{line_content}'")  # Debug print
        
        # Check if this line contains transaction data (starts with 4 spaces and has content)
        if line_content.strip() and line_content.startswith("    ") and " - " in line_content:
            print("Valid transaction line selected")  # Debug print
            self.transactions_text.tag_add("selected", line_start, line_end)
            self.transactions_text.selected_line = line_num
            
            # Count how many transaction lines come before this one
            transaction_count = 0
            for i in range(2, line_num + 1):  # Start from line 2 (after top padding)
                check_line = self.transactions_text.get(f"{i}.0", f"{i}.end")
                if check_line.strip() and check_line.startswith("    ") and " - " in check_line:
                    if i == line_num:
                        self.selected_transaction_index = transaction_count
                        print(f"Selected transaction index: {transaction_count}")  # Debug print
                        break
                    transaction_count += 1
        else:
            print("Invalid line selected")  # Debug print
            self.transactions_text.selected_line = None
            self.selected_transaction_index = None

    def delete_transaction(self):
        """Delete the selected transaction."""
        if not hasattr(self, 'selected_transaction_index') or self.selected_transaction_index is None:
            tk.messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return
        
        # Confirm deletion
        result = tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?")
        if not result:
            return
        
        try:
            # Read all transactions
            transactions = []
            with open(get_data_file_path("transactions_database.csv"), 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # Save header
                for row in reader:
                    if row and len(row) >= 5:
                        transactions.append(row)
            
            # Reverse to match display order
            transactions.reverse()
            
            # Get the transaction to delete
            if self.selected_transaction_index < len(transactions):
                transaction_to_delete = transactions[self.selected_transaction_index]
                flow_type = transaction_to_delete[0]
                label_name = transaction_to_delete[1]
                type_name = transaction_to_delete[3]
                
                # Remove the transaction from the list
                del transactions[self.selected_transaction_index]
                
                # Reverse back to original order for saving
                transactions.reverse()
                
                # Write back to file
                with open(get_data_file_path("transactions_database.csv"), 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)  # Write header
                    writer.writerows(transactions)
                
                # Update usage counts (decrement)
                self.decrement_usage_counts(flow_type, label_name, type_name)
                
                # Reload the display
                self.load_transactions()
                
                # Clear selection
                self.transactions_text.selected_line = None
                self.selected_transaction_index = None
                
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error deleting transaction: {e}")

    def decrement_usage_counts(self, flow_type, label_name, type_name):
        """Decrement usage counts for both label and type CSV files"""
        # Determine file names based on flow type
        if flow_type == "Expense":
            labels_file = get_data_file_path("expense_labels.csv")
            types_file = get_data_file_path("expense_types.csv")
        else:
            labels_file = get_data_file_path("income_labels.csv")
            types_file = get_data_file_path("income_types.csv")
        
        # Decrement label count
        self.decrement_label_count(labels_file, type_name, label_name)
        
        # Decrement type count
        self.decrement_type_count(types_file, type_name)

    def decrement_label_count(self, labels_file, type_name, label_name):
        """Decrement the count for a specific label"""
        try:
            # Read all labels
            labels = []
            with open(labels_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 3:
                        labels.append(row)
            
            # Find and update the specific label
            for i, (row_type, row_label, count) in enumerate(labels):
                if row_type == type_name and row_label == label_name:
                    new_count = max(0, int(count) - 1)  # Don't go below 0
                    labels[i] = [row_type, row_label, str(new_count)]
                    break
            
            # Write back to file
            with open(labels_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(labels)
                
        except Exception as e:
            print(f"Error updating label count in {labels_file}: {e}")

    def decrement_type_count(self, types_file, type_name):
        """Decrement the count for a specific type"""
        try:
            # Read all types
            types = []
            with open(types_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 2:
                        types.append(row)
            
            # Find and update the specific type
            for i, (row_type, count) in enumerate(types):
                if row_type == type_name:
                    new_count = max(0, int(count) - 1)  # Don't go below 0
                    types[i] = [row_type, str(new_count)]
                    break
            
            # Write back to file
            with open(types_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(types)
                
        except Exception as e:
            print(f"Error updating type count in {types_file}: {e}")

    def update_usage_counts(self, flow_type, label_name, type_name):
        """Update usage counts for both label and type CSV files"""
        # Determine file names based on flow type
        if flow_type == "Expense":
            labels_file = get_data_file_path("expense_labels.csv")
            types_file = get_data_file_path("expense_types.csv")
        else:
            labels_file = get_data_file_path("income_labels.csv")
            types_file = get_data_file_path("income_types.csv")
        
        # Update label count
        self.update_label_count(labels_file, type_name, label_name)
        
        # Update type count
        self.update_type_count(types_file, type_name)

    def update_label_count(self, labels_file, type_name, label_name):
        """Update the count for a specific label"""
        try:
            # Read all labels
            labels = []
            with open(labels_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 3:
                        labels.append(row)
            
            # Find and update the specific label
            for i, (row_type, row_label, count) in enumerate(labels):
                if row_type == type_name and row_label == label_name:
                    labels[i] = [row_type, row_label, str(int(count) + 1)]
                    break
            
            # Write back to file
            with open(labels_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(labels)
                
        except Exception as e:
            print(f"Error updating label count in {labels_file}: {e}")

    def update_type_count(self, types_file, type_name):
        """Update the count for a specific type"""
        try:
            # Read all types
            types = []
            with open(types_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 2:
                        types.append(row)
            
            # Find and update the specific type
            for i, (row_type, count) in enumerate(types):
                if row_type == type_name:
                    types[i] = [row_type, str(int(count) + 1)]
                    break
            
            # Write back to file
            with open(types_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(types)
                
        except Exception as e:
            print(f"Error updating type count in {types_file}: {e}")

import csv
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from ttkthemes import ThemedTk
from datetime import datetime

class LabelsAndTypes(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Main frame for the page
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a 2x2 grid layout
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Create four frames for the four sections
        expense_labels_frame = ttk.Frame(main_frame)
        expense_labels_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        expense_types_frame = ttk.Frame(main_frame)
        expense_types_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        income_labels_frame = ttk.Frame(main_frame)
        income_labels_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        income_types_frame = ttk.Frame(main_frame)
        income_types_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Setup content for each section
        self.setup_list_ui(expense_labels_frame, "Expense Labels", get_data_file_path("expense_labels.csv"))
        self.setup_list_ui(expense_types_frame, "Expense Types", get_data_file_path("expense_types.csv"))
        self.setup_list_ui(income_labels_frame, "Income Labels", get_data_file_path("income_labels.csv"))
        self.setup_list_ui(income_types_frame, "Income Types", get_data_file_path("income_types.csv"))

    def setup_list_ui(self, parent_frame, title, filename):
        """Helper function to create the UI for a list of items."""
        # Configure the parent frame to expand properly
        parent_frame.grid_rowconfigure(1, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        
        label = ttk.Label(parent_frame, text=title, font=("Arial", 14))
        label.grid(row=0, column=0, pady=5, sticky="ew")

        # Use Text widget instead of Listbox for rich text formatting
        text_widget = tk.Text(parent_frame, font=("Arial", 10), height=12, wrap=tk.WORD, 
                             cursor="hand2", state=tk.DISABLED)
        text_widget.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure tags for formatting
        text_widget.tag_configure("normal", font=("Arial", 10))
        text_widget.tag_configure("type", font=("Arial", 10, "italic"), foreground="gray")
        text_widget.tag_configure("selected", background="lightblue")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        text_widget.config(yscrollcommand=scrollbar.set)

        # Button frame for New and Delete buttons
        button_frame = ttk.Frame(parent_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        new_button = ttk.Button(button_frame, text="New", command=lambda: self.add_item(text_widget, filename))
        new_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text="Delete", command=lambda: self.delete_item(text_widget, filename))
        delete_button.pack(side=tk.LEFT, padx=5)

        # Store selection tracking
        text_widget.selected_line = None
        
        # Bind click events for selection
        text_widget.bind("<Button-1>", lambda e: self.on_text_click(text_widget, e))

        # Load initial data
        self.load_data(text_widget, filename)
        
        # Store widget for later access if needed
        setattr(self, f"{title.lower().replace(' ', '_')}_widget", text_widget)

    def on_text_click(self, text_widget, event):
        """Handle clicks on text widget for item selection."""
        # Clear previous selection
        text_widget.tag_remove("selected", "1.0", tk.END)
        
        # Get the line number where clicked
        index = text_widget.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        
        # Get the content of the line
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_content = text_widget.get(line_start, line_end).strip()
        
        # Only select non-empty lines
        if line_content:
            text_widget.tag_add("selected", line_start, line_end)
            text_widget.selected_line = line_num
        else:
            text_widget.selected_line = None

    def load_data(self, text_widget, filename):
        """Load data from a CSV file into a text widget."""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                first_item = True
                for row in reader:
                    if row:
                        # Add padding with empty line for top padding
                        if first_item:
                            text_widget.insert(tk.END, "\n")
                            first_item = False
                        
                        # Check if this is a label file (contains "labels" in filename)
                        if "labels" in filename and len(row) >= 3:
                            # Format: type,label,count - display as "label (type) [count]"
                            type_name = row[0]
                            label_name = row[1]
                            count = row[2]
                            text_widget.insert(tk.END, f"    {label_name} ", "normal")
                            text_widget.insert(tk.END, f"({type_name}) [{count}]", "type")
                        elif len(row) >= 2:
                            # For types: type,count - display as "type [count]"
                            type_name = row[0]
                            count = row[1]
                            text_widget.insert(tk.END, f"    {type_name} ", "normal")
                            text_widget.insert(tk.END, f"[{count}]", "type")
                        else:
                            # Fallback for old format
                            text_widget.insert(tk.END, f"    {row[0]}", "normal")
                        
                        text_widget.insert(tk.END, "\n\n")  # Empty line after each item
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(filename, 'w', newline='', encoding='utf-8'):
                pass
        
        text_widget.config(state=tk.DISABLED)

    def add_item(self, text_widget, filename):
        """Add a new item to the text widget and save it to the CSV file."""
        # Check if this is a label file
        if "labels" in filename:
            # Get the corresponding types file
            if "expense" in filename:
                types_filename = "expense_types.csv"
            else:
                types_filename = "income_types.csv"
            
            # Load available types
            available_types = []
            try:
                with open(types_filename, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and len(row) >= 1:
                            available_types.append(row[0])  # Just get the type name, ignore count
            except FileNotFoundError:
                tk.messagebox.showwarning("No Types", f"Please create some types in {types_filename} first.")
                return
            
            if not available_types:
                tk.messagebox.showwarning("No Types", "Please create some types first.")
                return
                
            # Show combined dialog for name and type selection
            result = self.show_label_dialog(available_types)
            if not result:
                return
            
            item_name, selected_type = result
            csv_data = [selected_type, item_name, "0"]  # Start with count of 0
        else:
            # For types, just ask for the item name
            item_name = simpledialog.askstring("New Type", "Enter the name of the new type:")
            if not item_name:
                return
            
            csv_data = [item_name, "0"]  # Start with count of 0
        
        # Add to CSV file
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(csv_data)
        except Exception as e:
            print(f"Error writing to {filename}: {e}")
        
        # Reload the display
        self.load_data(text_widget, filename)

    def show_label_dialog(self, available_types):
        """Show a combined dialog for entering label name and selecting type."""
        # Create a dialog
        dialog = tk.Toplevel()
        dialog.title("New Label")
        dialog.geometry("350x300")
        dialog.transient()
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"350x300+{x}+{y}")
        
        result = {'name': None, 'type': None}
        
        # Label name input
        ttk.Label(dialog, text="Label Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # Type selection
        ttk.Label(dialog, text="Select Type:").pack(pady=(15, 5))
        
        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE, height=8)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for type_name in available_types:
            listbox.insert(tk.END, type_name)
        
        def on_ok():
            name = name_entry.get().strip()
            selection = listbox.curselection()
            
            if not name:
                tk.messagebox.showwarning("Missing Name", "Please enter a label name.")
                return
            
            if not selection:
                tk.messagebox.showwarning("Missing Type", "Please select a type.")
                return
            
            result['name'] = name
            result['type'] = available_types[selection[0]]
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to OK
        dialog.bind('<Return>', lambda e: on_ok())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        if result['name'] and result['type']:
            return (result['name'], result['type'])
        return None

    def delete_item(self, text_widget, filename):
        """Delete the selected item from the text widget and CSV file."""
        if not hasattr(text_widget, 'selected_line') or text_widget.selected_line is None:
            tk.messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        
        # Get the content of the selected line
        line_start = f"{text_widget.selected_line}.0"
        line_end = f"{text_widget.selected_line}.end"
        line_content = text_widget.get(line_start, line_end).strip()
        
        if not line_content:
            tk.messagebox.showwarning("Invalid Selection", "Please select a valid item to delete.")
            return
        
        # Extract the actual item name for comparison
        if "labels" in filename and "(" in line_content and ")" in line_content:
            # For labels: extract label name from "    Label Name (Type Name) [Count]"
            # Remove leading spaces first
            item_text = line_content.strip()
            actual_item_name = item_text.split(" (")[0]
        elif "[" in line_content and "]" in line_content:
            # For types: extract type name from "    Type Name [Count]"
            item_text = line_content.strip()
            actual_item_name = item_text.split(" [")[0]
        else:
            # Fallback: just remove padding
            actual_item_name = line_content.strip()
        
        # Update the CSV file by rewriting it without the deleted item
        try:
            # Read all items except the one to delete
            items = []
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        # For labels, compare the label name (second column)
                        # For types, compare the type name (first column)
                        if "labels" in filename:
                            if len(row) >= 3 and row[1] != actual_item_name:
                                items.append(row)
                        else:
                            if len(row) >= 2 and row[0] != actual_item_name:
                                items.append(row)
            
            # Rewrite the file
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(items)
            
            # Reload the display
            self.load_data(text_widget, filename)
            
        except Exception as e:
            print(f"Error updating {filename}: {e}")


class Analytics(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Create a canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas (scrollbar first to avoid overlap)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Bind canvas resize to update scroll region
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Main title
        title_label = ttk.Label(self.scrollable_frame, text="Analytics", font=("Arial", 24))
        title_label.pack(pady=20)
        
        # Time period selection (applies to whole page)
        self.create_time_period_selection()
        
        # General Flow section
        self.create_general_flow_section()
        
        # Labels & Types section
        self.create_labels_types_section()
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize to update the scrollable frame width"""
        # Update the scrollable frame width to match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas.find_all()[0], width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_time_period_selection(self):
        """Create the time period selection that applies to the whole page"""
        period_frame = ttk.Frame(self.scrollable_frame)
        period_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(period_frame, text="Time Period:", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.period_var = tk.StringVar(value="All Time")
        period_options = ["Today", "Last 7 days", "Last 30 days", "Last 12 months", "All Time"]
        period_dropdown = ttk.Combobox(period_frame, textvariable=self.period_var, values=period_options, 
                                     state="readonly", width=15, font=("Arial", 12))
        period_dropdown.pack(side=tk.LEFT)
        period_dropdown.bind("<<ComboboxSelected>>", self.update_all_analytics)
        
        # Separator
        separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)
    
    def create_general_flow_section(self):
        """Create the General Flow analytics section"""
        # Section frame
        flow_frame = ttk.LabelFrame(self.scrollable_frame, text="General Flow")
        flow_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Main analytics frame with two columns
        analytics_frame = ttk.Frame(flow_frame)
        analytics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left column - Totals
        left_frame = ttk.Frame(analytics_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        ttk.Label(left_frame, text="TOTALS", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Total expenses
        self.total_expenses_frame = ttk.Frame(left_frame)
        self.total_expenses_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.total_expenses_frame, text="Total Expenses:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.total_expenses_label = ttk.Label(self.total_expenses_frame, text="₺0.00", 
                                            font=("Arial", 11, "bold"), foreground="darkred")
        self.total_expenses_label.pack(side=tk.RIGHT)
        
        # Total income
        self.total_income_frame = ttk.Frame(left_frame)
        self.total_income_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.total_income_frame, text="Total Income:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.total_income_label = ttk.Label(self.total_income_frame, text="₺0.00", 
                                          font=("Arial", 11, "bold"), foreground="darkgreen")
        self.total_income_label.pack(side=tk.RIGHT)
        
        # Total balance
        self.total_balance_frame = ttk.Frame(left_frame)
        self.total_balance_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.total_balance_frame, text="Total Balance:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.total_balance_label = ttk.Label(self.total_balance_frame, text="₺0.00", 
                                           font=("Arial", 11, "bold"))
        self.total_balance_label.pack(side=tk.RIGHT)
        
        # Right column - Averages
        right_frame = ttk.Frame(analytics_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="DAILY AVERAGES", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Average daily expenses
        self.avg_expenses_frame = ttk.Frame(right_frame)
        self.avg_expenses_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.avg_expenses_frame, text="Average Daily Expense:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.avg_expenses_label = ttk.Label(self.avg_expenses_frame, text="₺0.00", 
                                          font=("Arial", 11, "bold"), foreground="darkred")
        self.avg_expenses_label.pack(side=tk.RIGHT)
        
        # Average daily income
        self.avg_income_frame = ttk.Frame(right_frame)
        self.avg_income_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.avg_income_frame, text="Average Daily Income:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.avg_income_label = ttk.Label(self.avg_income_frame, text="₺0.00", 
                                        font=("Arial", 11, "bold"), foreground="darkgreen")
        self.avg_income_label.pack(side=tk.RIGHT)
        
        # Average daily balance
        self.avg_balance_frame = ttk.Frame(right_frame)
        self.avg_balance_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.avg_balance_frame, text="Average Daily Balance:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.avg_balance_label = ttk.Label(self.avg_balance_frame, text="₺0.00", 
                                         font=("Arial", 11, "bold"))
        self.avg_balance_label.pack(side=tk.RIGHT)
        
        # Load initial data
        self.update_general_flow()
    
    def create_labels_types_section(self):
        """Create the Labels & Types analytics section"""
        # Section frame
        labels_types_frame = ttk.LabelFrame(self.scrollable_frame, text="Labels & Types")
        labels_types_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Main content frame
        content_frame = ttk.Frame(labels_types_frame)
        content_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Most Common Expenses By Label
        self.create_tabbed_subsection(content_frame, "Most Common Expenses By Label", "expense_label")
        
        # Most Common Expenses By Type
        self.create_tabbed_subsection(content_frame, "Most Common Expenses By Type", "expense_type")
        
        # Most Common Incomes By Label
        self.create_tabbed_subsection(content_frame, "Most Common Incomes By Label", "income_label")
        
        # Most Common Incomes By Type
        self.create_tabbed_subsection(content_frame, "Most Common Incomes By Type", "income_type")
        
        # Load initial data for this section
        self.update_labels_types()
    
    def create_tabbed_subsection(self, parent, title, section_id):
        """Create a tabbed subsection with Numerical and Graphs tabs"""
        # Title
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(title_frame, text=title, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Tab buttons
        tab_frame = ttk.Frame(title_frame)
        tab_frame.pack(side=tk.RIGHT)
        
        # Create tab variable for this section
        tab_var = tk.StringVar(value="numerical")
        setattr(self, f"{section_id}_tab_var", tab_var)
        
        # Numerical tab button
        numerical_btn = ttk.Button(tab_frame, text="Numerical", 
                                 command=lambda: self.switch_tab(section_id, "numerical"))
        numerical_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Graphs tab button
        graphs_btn = ttk.Button(tab_frame, text="Graphs", 
                              command=lambda: self.switch_tab(section_id, "graphs"))
        graphs_btn.pack(side=tk.LEFT)
        
        # Store tab buttons for styling
        setattr(self, f"{section_id}_numerical_btn", numerical_btn)
        setattr(self, f"{section_id}_graphs_btn", graphs_btn)
        
        # Content frame for this subsection (initially adaptable)
        subsection_frame = ttk.Frame(parent)
        subsection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Store reference to subsection frame for dynamic height control
        setattr(self, f"{section_id}_subsection_frame", subsection_frame)
        
        # Numerical content frame
        numerical_frame = ttk.Frame(subsection_frame)
        numerical_frame.pack(fill=tk.BOTH, expand=True)
        setattr(self, f"{section_id}_numerical_frame", numerical_frame)
        
        # Graphs content frame (hidden by default)
        graphs_frame = ttk.Frame(subsection_frame)
        setattr(self, f"{section_id}_graphs_frame", graphs_frame)
        
        # Create 5 rows for numerical data
        rows = []
        for i in range(5):
            row_frame = ttk.Frame(numerical_frame)
            row_frame.pack(fill=tk.X, pady=1)
            
            label_text = ttk.Label(row_frame, text="", font=("Arial", 12))
            label_text.pack(side=tk.LEFT)
            
            stats_text = ttk.Label(row_frame, text="", font=("Arial", 12))
            stats_text.pack(side=tk.RIGHT)
            
            rows.append((label_text, stats_text))
        
        # Store rows for this section
        setattr(self, f"{section_id}_rows", rows)
        
        # Create chart frame for graphs tab
        self.create_chart_frame(graphs_frame, section_id)
        
        # Set initial tab state
        self.switch_tab(section_id, "numerical")
    
    def switch_tab(self, section_id, tab_type):
        """Switch between numerical and graphs tabs for a section"""
        # Update tab variable
        tab_var = getattr(self, f"{section_id}_tab_var")
        tab_var.set(tab_type)
        
        # Get frames
        numerical_frame = getattr(self, f"{section_id}_numerical_frame")
        graphs_frame = getattr(self, f"{section_id}_graphs_frame")
        subsection_frame = getattr(self, f"{section_id}_subsection_frame")
        
        # Get buttons
        numerical_btn = getattr(self, f"{section_id}_numerical_btn")
        graphs_btn = getattr(self, f"{section_id}_graphs_btn")
        
        if tab_type == "numerical":
            # Show numerical, hide graphs
            numerical_frame.pack(fill=tk.BOTH, expand=True)
            graphs_frame.pack_forget()
            
            # Make frame adaptable (remove fixed height)
            subsection_frame.config(height=1)  # Minimal height
            subsection_frame.pack_propagate(True)  # Allow frame to adapt to content
            
            # Update button states
            numerical_btn.config(state="disabled")
            graphs_btn.config(state="normal")
        else:
            # Show graphs, hide numerical
            graphs_frame.pack(fill=tk.BOTH, expand=True)
            numerical_frame.pack_forget()
            
            # Set fixed height for graphs
            subsection_frame.config(height=300)
            subsection_frame.pack_propagate(False)  # Prevent frame from shrinking
            
            # Update button states
            graphs_btn.config(state="disabled")
            numerical_btn.config(state="normal")
            
            # Update charts when switching to graphs tab
            self.update_section_charts(section_id)
    
    def create_chart_frame(self, parent, section_id):
        """Create chart frame with side-by-side bar and pie charts"""
        # Main chart container
        chart_container = ttk.Frame(parent)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights for equal distribution
        chart_container.grid_columnconfigure(0, weight=1)
        chart_container.grid_columnconfigure(1, weight=1)
        chart_container.grid_rowconfigure(0, weight=1)
        
        # Left frame for bar chart
        bar_chart_frame = ttk.LabelFrame(chart_container, text="Bar Chart")
        bar_chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=0)
        
        # Right frame for pie chart
        pie_chart_frame = ttk.LabelFrame(chart_container, text="Pie Chart")
        pie_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 0), pady=0)
        
        # Store references
        setattr(self, f"{section_id}_bar_chart_frame", bar_chart_frame)
        setattr(self, f"{section_id}_pie_chart_frame", pie_chart_frame)
        
        # Create both charts
        self.create_both_charts(section_id)
    
    def create_both_charts(self, section_id):
        """Create both interactive bar and pie charts side by side"""
        # Get data for this section
        data = self.get_section_data(section_id)
        
        # Get chart frames
        bar_frame = getattr(self, f"{section_id}_bar_chart_frame")
        pie_frame = getattr(self, f"{section_id}_pie_chart_frame")
        
        # Clear previous charts
        for widget in bar_frame.winfo_children():
            widget.destroy()
        for widget in pie_frame.winfo_children():
            widget.destroy()
        
        if not data:
            # Show no data message in both frames
            no_data_bar = ttk.Label(bar_frame, text="No data available", 
                                  font=("Arial", 10, "italic"), foreground="gray")
            no_data_bar.pack(expand=True)
            
            no_data_pie = ttk.Label(pie_frame, text="No data available", 
                                  font=("Arial", 10, "italic"), foreground="gray")
            no_data_pie.pack(expand=True)
            return
        
        # Get colors for items
        colors = self.get_chart_colors(len(data))
        
        # Create interactive bar chart
        bar_fig = Figure(figsize=(4, 2.5), dpi=80)
        bar_ax = bar_fig.add_subplot(111)
        bar_canvas = FigureCanvasTkAgg(bar_fig, bar_frame)
        self.create_interactive_bar_chart(bar_ax, bar_canvas, data, colors)
        
        bar_canvas.draw()
        bar_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create interactive pie chart
        pie_fig = Figure(figsize=(4, 2.5), dpi=80)
        pie_ax = pie_fig.add_subplot(111)
        pie_canvas = FigureCanvasTkAgg(pie_fig, pie_frame)
        self.create_interactive_pie_chart(pie_ax, pie_canvas, data, colors)
        
        pie_canvas.draw()
        pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def get_section_data(self, section_id):
        """Get data for a specific section to create charts"""
        rows = getattr(self, f"{section_id}_rows", [])
        data = []
        
        for label_widget, stats_widget in rows:
            label_text = label_widget.cget("text")
            stats_text = stats_widget.cget("text")
            
            if label_text and stats_text:
                # Extract percentage and amount from stats text (format: "X.X% | ₺Y.YY | ₺Z.ZZ/day")
                try:
                    # Remove the number prefix from label (e.g., "1. Food" -> "Food")
                    clean_label = label_text.split('. ', 1)[1] if '. ' in label_text else label_text
                    
                    # Extract percentage
                    percentage_str = stats_text.split('%')[0]
                    percentage = float(percentage_str)
                    
                    # Extract total amount
                    amount_part = stats_text.split('₺')[1].split(' |')[0]
                    amount = float(amount_part)
                    
                    data.append((clean_label, amount))
                except (ValueError, IndexError):
                    continue
        
        return data
    
    def get_chart_colors(self, num_colors):
        """Generate distinct colors for chart items"""
        if num_colors <= 10:
            # Use predefined distinct colors for small datasets
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', 
                     '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43']
            return colors[:num_colors]
        else:
            # Generate colors using matplotlib colormap for larger datasets
            cmap = plt.cm.tab20
            return [cmap(i / num_colors) for i in range(num_colors)]
    
    def create_interactive_bar_chart(self, ax, canvas, data, colors):
        """Create an interactive bar chart with hover tooltips"""
        labels, values = zip(*data) if data else ([], [])
        
        # Create bars with no labels or text
        bars = ax.bar(range(len(labels)), values, color=colors)
        
        # Remove all text elements
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_title('')
        
        # Remove spines for cleaner look
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Create tooltip
        tooltip = ax.annotate('', xy=(0, 0), xytext=(10, 10), 
                            textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.8),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                            fontsize=9, visible=False)
        
        def on_hover(event):
            if event.inaxes == ax:
                for i, bar in enumerate(bars):
                    if bar.contains(event)[0]:
                        # Show tooltip with item info
                        label = labels[i]
                        value = values[i]
                        percentage = (value / sum(values) * 100) if sum(values) > 0 else 0
                        
                        tooltip.set_text(f'{label}\n₺{value:.2f}\n{percentage:.1f}%')
                        
                        # Get bar properties
                        bar_x = bar.get_x() + bar.get_width()/2
                        bar_height = bar.get_height()
                        max_value = max(values)
                        min_value = min(values)
                        
                        # Find index of smallest bar
                        min_index = values.index(min_value)
                        
                        # Check if this is the tallest bar (within 10% of max)
                        is_tall_bar = bar_height >= max_value * 0.9
                        
                        # Check if this is the smallest bar by comparing indices
                        is_smallest_bar = (i == min_index)
                        
                        # Set tooltip position
                        tooltip.xy = (bar_x, bar_height if not is_tall_bar else 0)
                        
                        if is_smallest_bar:
                            # Smallest bar: always position to the left
                            if is_tall_bar:
                                tooltip.xytext = (-80, -50)  # Left and down
                            else:
                                tooltip.xytext = (-80, 10)   # Left and up
                        elif is_tall_bar:
                            # Tallest bar (not smallest): position down
                            tooltip.xytext = (10, -50)
                        else:
                            # Regular bars: position up and right (default)
                            tooltip.xytext = (10, 10)
                        
                        tooltip.set_visible(True)
                        canvas.draw_idle()
                        return
                
                # Hide tooltip if not hovering over any bar
                tooltip.set_visible(False)
                canvas.draw_idle()
        
        def on_leave(event):
            tooltip.set_visible(False)
            canvas.draw_idle()
        
        # Connect events
        canvas.mpl_connect('motion_notify_event', on_hover)
        canvas.mpl_connect('axes_leave_event', on_leave)
        
        ax.figure.tight_layout()
    
    def create_interactive_pie_chart(self, ax, canvas, data, colors):
        """Create an interactive pie chart with hover tooltips"""
        labels, values = zip(*data) if data else ([], [])
        
        # Create pie chart with no labels or text
        wedges = ax.pie(values, colors=colors, startangle=90)[0]
        
        ax.set_title('')
        
        # Create tooltip
        tooltip = ax.annotate('', xy=(0, 0), xytext=(10, 10), 
                            textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.8),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                            fontsize=9, visible=False)
        
        def on_hover(event):
            if event.inaxes == ax:
                for i, wedge in enumerate(wedges):
                    if wedge.contains(event)[0]:
                        # Show tooltip with item info
                        label = labels[i]
                        value = values[i]
                        percentage = (value / sum(values) * 100) if sum(values) > 0 else 0
                        
                        tooltip.set_text(f'{label}\n₺{value:.2f}\n{percentage:.1f}%')
                        tooltip.xy = (event.xdata, event.ydata)
                        tooltip.set_visible(True)
                        canvas.draw_idle()
                        return
                
                # Hide tooltip if not hovering over any wedge
                tooltip.set_visible(False)
                canvas.draw_idle()
        
        def on_leave(event):
            tooltip.set_visible(False)
            canvas.draw_idle()
        
        # Connect events
        canvas.mpl_connect('motion_notify_event', on_hover)
        canvas.mpl_connect('axes_leave_event', on_leave)
    
    def update_section_charts(self, section_id):
        """Update charts for a section when data changes"""
        # Only update if charts tab is currently active
        tab_var = getattr(self, f"{section_id}_tab_var")
        if tab_var.get() == "graphs":
            # Refresh both charts
            self.create_both_charts(section_id)
    
    def update_all_analytics(self, event=None):
        """Update all analytics based on selected time period"""
        self.update_general_flow()
        self.update_labels_types()
    
    def update_general_flow(self):
        """Update general flow analytics"""
    
    def update_general_flow(self):
        """Update general flow analytics"""
        period = self.period_var.get()
        
        # Get filtered transactions
        transactions = self.get_filtered_transactions(period)
        
        # Calculate metrics
        total_expenses, total_income = self.calculate_totals(transactions)
        total_balance = total_income - total_expenses
        
        # Calculate averages
        days_in_period = self.get_days_in_period(period, transactions)
        avg_expenses = total_expenses / days_in_period if days_in_period > 0 else 0
        avg_income = total_income / days_in_period if days_in_period > 0 else 0
        avg_balance = total_balance / days_in_period if days_in_period > 0 else 0
        
        # Update labels
        self.total_expenses_label.config(text=f"₺{total_expenses:.2f}")
        self.total_income_label.config(text=f"₺{total_income:.2f}")
        self.total_balance_label.config(text=f"₺{total_balance:.2f}")
        
        self.avg_expenses_label.config(text=f"₺{avg_expenses:.2f}")
        self.avg_income_label.config(text=f"₺{avg_income:.2f}")
        self.avg_balance_label.config(text=f"₺{avg_balance:.2f}")
        
        # Update balance colors based on positive/negative
        balance_color = "darkgreen" if total_balance >= 0 else "darkred"
        self.total_balance_label.config(foreground=balance_color)
        
        avg_balance_color = "darkgreen" if avg_balance >= 0 else "darkred"
        self.avg_balance_label.config(foreground=avg_balance_color)
    
    def update_labels_types(self):
        """Update labels & types analytics"""
        period = self.period_var.get()
        transactions = self.get_filtered_transactions(period)
        days_in_period = self.get_days_in_period(period, transactions)
        
        # Calculate statistics for each category
        expense_label_stats = self.calculate_label_stats(transactions, "Expense")
        expense_type_stats = self.calculate_type_stats(transactions, "Expense")
        income_label_stats = self.calculate_label_stats(transactions, "Income")
        income_type_stats = self.calculate_type_stats(transactions, "Income")
        
        # Update display for each section
        self.display_stats_in_rows(self.expense_label_rows, expense_label_stats, days_in_period, "darkred")
        self.display_stats_in_rows(self.expense_type_rows, expense_type_stats, days_in_period, "darkred")
        self.display_stats_in_rows(self.income_label_rows, income_label_stats, days_in_period, "darkgreen")
        self.display_stats_in_rows(self.income_type_rows, income_type_stats, days_in_period, "darkgreen")
        
        # Update charts for all sections
        self.update_section_charts("expense_label")
        self.update_section_charts("expense_type")
        self.update_section_charts("income_label")
        self.update_section_charts("income_type")
    
    def calculate_label_stats(self, transactions, flow_type):
        """Calculate statistics for labels"""
        label_totals = {}
        total_amount = 0
        
        for transaction in transactions:
            if len(transaction) >= 5 and transaction[0] == flow_type:
                try:
                    label = transaction[1]
                    amount = float(transaction[2])
                    label_totals[label] = label_totals.get(label, 0) + amount
                    total_amount += amount
                except (ValueError, IndexError):
                    continue
        
        # Sort by amount and get top 5
        sorted_labels = sorted(label_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate percentages
        stats = []
        for label, amount in sorted_labels:
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            stats.append((label, amount, percentage))
        
        return stats
    
    def calculate_type_stats(self, transactions, flow_type):
        """Calculate statistics for types"""
        type_totals = {}
        total_amount = 0
        
        for transaction in transactions:
            if len(transaction) >= 5 and transaction[0] == flow_type:
                try:
                    type_name = transaction[3]
                    amount = float(transaction[2])
                    type_totals[type_name] = type_totals.get(type_name, 0) + amount
                    total_amount += amount
                except (ValueError, IndexError):
                    continue
        
        # Sort by amount and get top 5
        sorted_types = sorted(type_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate percentages
        stats = []
        for type_name, amount in sorted_types:
            percentage = (amount / total_amount * 100) if total_amount > 0 else 0
            stats.append((type_name, amount, percentage))
        
        return stats
    
    def display_stats_in_rows(self, rows, stats, days_in_period, color):
        """Display statistics in the allocated rows"""
        # Clear all rows first
        for label_widget, stats_widget in rows:
            label_widget.config(text="", foreground="black")
            stats_widget.config(text="", foreground="black")
        
        # Fill rows with data
        for i, (name, total, percentage) in enumerate(stats[:5]):  # Limit to 5 items
            if i < len(rows):
                daily_avg = total / days_in_period if days_in_period > 0 else 0
                
                # Set label name
                rows[i][0].config(text=f"{i+1}. {name}", foreground=color)
                
                # Set statistics (percentage, total, daily average)
                stats_text = f"{percentage:.1f}% | ₺{total:.2f} | ₺{daily_avg:.2f}/day"
                rows[i][1].config(text=stats_text, foreground=color)
    
    def get_filtered_transactions(self, period):
        """Get transactions filtered by the selected time period"""
        try:
            with open(get_data_file_path("transactions_database.csv"), 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                all_transactions = [row for row in reader if row and len(row) >= 5]
        except FileNotFoundError:
            return []
        
        if period == "All Time":
            return all_transactions
        
        # Get current date and calculate cutoff date
        current_date = datetime.now()
        
        if period == "Today":
            cutoff_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "Last 7 days":
            cutoff_date = current_date - timedelta(days=7)
        elif period == "Last 30 days":
            cutoff_date = current_date - timedelta(days=30)
        elif period == "Last 12 months":
            cutoff_date = current_date - timedelta(days=365)
        else:
            return all_transactions
        
        # Filter transactions
        filtered = []
        for transaction in all_transactions:
            try:
                transaction_date = datetime.strptime(transaction[4], "%d/%m/%Y")
                if transaction_date >= cutoff_date:
                    filtered.append(transaction)
            except ValueError:
                continue  # Skip transactions with invalid dates
        
        return filtered
    
    def calculate_totals(self, transactions):
        """Calculate total expenses and income from transactions"""
        total_expenses = 0.0
        total_income = 0.0
        
        for transaction in transactions:
            try:
                flow_type = transaction[0]
                amount = float(transaction[2])
                
                if flow_type == "Expense":
                    total_expenses += amount
                elif flow_type == "Income":
                    total_income += amount
            except (ValueError, IndexError):
                continue  # Skip invalid transactions
        
        return total_expenses, total_income
    
    def get_days_in_period(self, period, transactions):
        """Calculate number of days in the selected period based on actual data availability"""
        current_date = datetime.now()
        
        if period == "Today":
            return 1
        
        # Get all transaction dates to find the earliest one
        all_transaction_dates = []
        try:
            with open(get_data_file_path("transactions_database.csv"), 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if row and len(row) >= 5:
                        try:
                            date = datetime.strptime(row[4], "%d/%m/%Y")
                            all_transaction_dates.append(date)
                        except ValueError:
                            continue
        except FileNotFoundError:
            return 1
        
        if not all_transaction_dates:
            return 1
        
        earliest_transaction_date = min(all_transaction_dates)
        
        # Calculate the theoretical start date for the period
        if period == "Last 7 days":
            theoretical_start = current_date - timedelta(days=7)
        elif period == "Last 30 days":
            theoretical_start = current_date - timedelta(days=30)
        elif period == "Last 12 months":
            theoretical_start = current_date - timedelta(days=365)
        elif period == "All Time":
            # For "All Time", use actual data range
            if transactions:
                dates = []
                for transaction in transactions:
                    try:
                        date = datetime.strptime(transaction[4], "%d/%m/%Y")
                        dates.append(date)
                    except ValueError:
                        continue
                
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    days = (max_date - min_date).days + 1
                    return max(1, days)
            return 1
        else:
            return 1
        
        # Use the later of the theoretical start date or the earliest transaction date
        actual_start_date = max(theoretical_start, earliest_transaction_date)
        
        # Calculate days from actual start to now
        days = (current_date - actual_start_date).days + 1
        
        return max(1, days)  # At least 1 day

class Settings(Page):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        label = ttk.Label(self, text="Settings Page", font=("Arial", 24))
        label.pack(pady=20, padx=20)

if __name__ == "__main__":
    app = BudgetTrackerApp()
    app.mainloop()
